"""Weatherman Model Context Protocol API.

This module exposes a minimal FastAPI application that models a "weatherman"
service following the Model Context Protocol (MCP).  The API advertises a
single tool, ``getWeather``, via a ``/.well-known/mcp.json`` discovery
endpoint and provides a dummy implementation of the tool.  Although the
service does not talk to a real weather backend, it returns deterministic
results that make it easy to test end-to-end MCP flows.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Weatherman MCP API",
    version="1.0.0",
    description=(
        "A sample implementation of the Model Context Protocol for a simple "
        "weather service."
    ),
)


SUPPORTED_UNITS: tuple[Literal["celsius", "fahrenheit"], ...] = (
    "celsius",
    "fahrenheit",
)


class WeatherRequest(BaseModel):
    """Schema for the ``getWeather`` tool input."""

    location: str = Field(
        ..., description="Name of the city or location to look up weather for."
    )
    unit: Literal["celsius", "fahrenheit"] = Field(
        "celsius",
        description="Desired temperature unit in the response.",
    )


class WeatherResponse(BaseModel):
    """Schema describing the dummy ``getWeather`` tool output."""

    location: str
    temperature: float = Field(description="Temperature value in the requested unit.")
    unit: Literal["celsius", "fahrenheit"]
    condition: str = Field(description="Short human readable weather summary.")
    observation_time: datetime = Field(
        description="Timestamp indicating when the dummy observation was generated."
    )
    note: str = Field(description="Indicates that the response is not real data.")


class MCPManifestTool(BaseModel):
    """Represents a tool description for the MCP manifest."""

    name: str
    description: str
    input_schema: dict[str, object] = Field(alias="inputSchema")

    class Config:
        populate_by_name = True


class MCPManifest(BaseModel):
    """Model Context Protocol manifest response."""

    name: str
    version: str
    description: str
    tools: list[MCPManifestTool]


def _deterministic_temperature(location: str) -> tuple[float, str]:
    """Generate a deterministic dummy temperature and condition for a location."""

    digest = hashlib.sha256(location.encode("utf-8")).hexdigest()
    numeric = int(digest[:8], 16)
    temperature_celsius = 10.0 + (numeric % 2000) / 100  # 10.00°C .. 29.99°C
    conditions = (
        "sunny",
        "cloudy",
        "partly cloudy",
        "light rain",
        "stormy",
        "foggy",
        "snowy",
    )
    condition = conditions[numeric % len(conditions)]
    return temperature_celsius, condition


@app.get("/.well-known/mcp.json", response_model=MCPManifest)
async def mcp_manifest() -> MCPManifest:
    """Expose the MCP manifest so clients can discover available tools."""

    return MCPManifest(
        name="weatherman",
        version="1.0.0",
        description="Dummy Model Context Protocol weather service.",
        tools=[
            MCPManifestTool(
                name="getWeather",
                description="Retrieve synthetic weather information for a location.",
                inputSchema=WeatherRequest.model_json_schema(),
            )
        ],
    )


@app.post("/mcp/v1/getWeather", response_model=WeatherResponse)
async def get_weather(payload: WeatherRequest) -> WeatherResponse:
    """Return deterministic fake weather information for the requested location."""

    if payload.unit not in SUPPORTED_UNITS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported unit '{payload.unit}'. Valid options: {SUPPORTED_UNITS}",
        )

    temperature_celsius, condition = _deterministic_temperature(payload.location)

    if payload.unit == "fahrenheit":
        temperature = round(temperature_celsius * 9 / 5 + 32, 2)
    else:
        temperature = round(temperature_celsius, 2)

    return WeatherResponse(
        location=payload.location,
        temperature=temperature,
        unit=payload.unit,
        condition=condition,
        observation_time=datetime.now(timezone.utc),
        note=(
            "This weather data is generated deterministically for testing and "
            "does not reflect real-world conditions."
        ),
    )


@app.get("/healthz")
async def healthcheck() -> dict[str, str]:
    """Lightweight health endpoint for container orchestrators."""

    return {"status": "ok"}


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    import uvicorn

    uvicorn.run("first_gen_ai.weatherman_mcp:app", host="0.0.0.0", port=8000, reload=False)
