# api/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any

from . import schemas
from .db import SessionLocal, init_db, ModelRecord, create_model_record
from .walrus_client import upload_artifact
from .config import (
    DATASET_ID,
    DATASET_HASH,
    DATASET_SYMBOL,
    DATASET_TIMEFRAME,
    DATASET_RANGE,
    ARTIFACT_VERSION,
    ESL_VERSION,
    ENGINE_VERSION,
    DATASET_VERSION,
)

# Import your engine pieces
from engine.backtester import run_backtest
from engine.serialization import build_model_artifact


app = FastAPI(title="EverythingSignal API", version="0.1.0")

# Allow local dev + simple frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency: DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()


def _build_dataset_info() -> schemas.DatasetInfo:
    return schemas.DatasetInfo(
        id=DATASET_ID,
        hash=DATASET_HASH,
        symbol=DATASET_SYMBOL,
        timeframe=DATASET_TIMEFRAME,
        range=DATASET_RANGE,
    )


def _wrap_v02_artifact(
    model_json: Dict[str, Any],
    artifact_v01: Dict[str, Any],
    extra_metadata: Dict[str, Any],
) -> schemas.Artifact:
    """
    Your engine's build_model_artifact currently returns a v0.1-style dict
    with model + backtest + metadata baked in.

    Here we adapt it into the v0.2 schema with dataset + zk blocks.
    """
    dataset_info = _build_dataset_info()

    # artifact_v01["backtest"] is already JSON (from your serialization.py)
    backtest_json = artifact_v01["backtest"]
    # Pydantic will validate/reshape
    backtest = schemas.BacktestJSON(**backtest_json)

    # Merge metadata
    metadata = dict(artifact_v01.get("metadata", {}))
    metadata.update(extra_metadata or {})
    metadata.update(
        {
            "engine_version": ENGINE_VERSION,
            "esl_version": ESL_VERSION,
            "dataset_version": DATASET_VERSION,
        }
    )

    zk_info = schemas.ZKInfo(
        proof_system="risc0",
        program_id=None,
        proof=None,
        public_journal=None,
    )

    return schemas.Artifact(
        version=ARTIFACT_VERSION,
        model=model_json,
        backtest=backtest,
        dataset=dataset_info,
        zk=zk_info,
        metadata=metadata,
    )


@app.post("/simulate", response_model=schemas.SimulateResponse)
def simulate(
    req: schemas.SimulateRequest,
):
    """
    Run ESL + backtest, return a full artifact (not stored, no Walrus).
    """
    model_json = req.model

    # In the future: you’ll load the canonical dataset here according to docs/dataset_spec.md
    # For now you likely already have this in engine/example_usage.
    # Here we'll assume you have a helper to load your BTC-USDT 1D DataFrame.
    from engine.dataset import load_dataset

    df = load_dataset()
    backtest_result = run_backtest(model_json, df)


    # Build v0.1 artifact using your existing helper
    artifact_v01 = build_model_artifact(
        model_json,
        backtest_result,
        metadata=req.metadata or {},
    )

    # Wrap into v0.2 artifact (with dataset + zk placeholders)
    artifact_v02 = _wrap_v02_artifact(
        model_json=model_json,
        artifact_v01=artifact_v01,
        extra_metadata=req.metadata or {},
    )

    return schemas.SimulateResponse(artifact=artifact_v02)


@app.post("/publish", response_model=schemas.PublishResponse)
def publish(
    req: schemas.PublishRequest,
    db: Session = Depends(get_db),
):
    """
    Run simulation, build artifact, upload to Walrus (stub), and
    store metadata + walrus artifact ID in SQLite.
    """
    model_json = req.model

    from engine.dataset import load_dataset

    df = load_dataset()
    backtest_result = run_backtest(model_json, df)



    artifact_v01 = build_model_artifact(
        model_json,
        backtest_result,
        metadata={
            "name": req.name,
            "description": req.description,
            "tags": req.tags,
        },
    )

    artifact_v02 = _wrap_v02_artifact(
        model_json=model_json,
        artifact_v01=artifact_v01,
        extra_metadata={
            "name": req.name,
            "description": req.description,
            "tags": req.tags,
        },
    )

    # Upload to Walrus (stub for now)
    artifact_dict = artifact_v02.model_dump()
    artifact_id = upload_artifact(artifact_dict)

    # Store in SQLite
    metrics = artifact_v02.backtest.metrics
    model_record = create_model_record(
        db,
        name=req.name,
        description=req.description,
        tags=req.tags or [],
        artifact_id=artifact_id,
        summary_metrics=metrics,
    )

    return schemas.PublishResponse(
        model_id=model_record.model_id,
        artifact_id=artifact_id,
        artifact=artifact_v02,
    )


@app.get("/models/{model_id}")
def get_model(model_id: str, db: Session = Depends(get_db)):
    """
    Fetch model metadata from SQLite (no artifact content).
    """
    record = (
        db.query(ModelRecord)
        .filter(ModelRecord.model_id == model_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Model not found")

    import json

    return {
        "model_id": record.model_id,
        "name": record.name,
        "description": record.description,
        "tags": json.loads(record.tags or "[]"),
        "artifact_id": record.artifact_id,
        "summary_metrics": json.loads(record.summary_metrics or "{}"),
        "created_at": record.created_at.isoformat(),
    }


@app.get("/models/{model_id}/artifact", response_model=schemas.Artifact)
def get_model_artifact(model_id: str, db: Session = Depends(get_db)):
    """
    Fetch full artifact. For now, we don't refetch from Walrus;
    we rely on the fact that we just uploaded and could also have
    stored it locally if needed.

    In a real integration, you'd:
      - read record.artifact_id
      - fetch JSON from Walrus using that ID
      - return it as Artifact
    """
    record = (
        db.query(ModelRecord)
        .filter(ModelRecord.model_id == model_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Model not found")

    # TODO: integrate real Walrus fetch here.
    # For now, this endpoint is a placeholder; you can adapt it once
    # you store artifacts locally or wire up Walrus.
    raise HTTPException(
        status_code=501,
        detail="Artifact retrieval not implemented yet (wire to Walrus).",
    )
