# api/schemas.py

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SimulateRequest(BaseModel):
    model: Dict[str, Any] = Field(..., description="ESL JSON operator tree")
    metadata: Optional[Dict[str, Any]] = None


class PublishRequest(BaseModel):
    model: Dict[str, Any]
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class DatasetInfo(BaseModel):
    id: str
    hash: str
    symbol: str
    timeframe: str
    range: str


class BacktestMetrics(BaseModel):
    sharpe: float
    volatility: float
    max_drawdown: float
    cagr: float
    win_rate: float


class TimeSeriesJSON(BaseModel):
    index: List[str]
    values: List[Optional[float]]


class BacktestJSON(BaseModel):
    metrics: Dict[str, float]
    signal: TimeSeriesJSON
    strategy_returns: TimeSeriesJSON
    cumulative_returns: TimeSeriesJSON


class ZKInfo(BaseModel):
    proof_system: str
    program_id: Optional[str] = None
    proof: Optional[str] = None
    public_journal: Optional[Dict[str, Any]] = None


class Artifact(BaseModel):
    version: str
    model: Dict[str, Any]
    backtest: BacktestJSON
    dataset: DatasetInfo
    zk: ZKInfo
    metadata: Dict[str, Any]


class SimulateResponse(BaseModel):
    artifact: Artifact


class PublishResponse(BaseModel):
    model_id: str
    artifact_id: str
    artifact: Artifact
