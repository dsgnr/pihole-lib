"""Base model classes."""

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base model with Pydantic v2 config."""

    model_config = ConfigDict(populate_by_name=True)


class TimedResponse(StrictModel):
    """Base for API responses with timing information."""

    took: float = Field(..., description="Time taken to process the request in seconds")


class ProcessedSuccess(StrictModel):
    """Generic success item in processing result."""

    item: str = Field(..., description="Item that was successfully processed")


class ProcessedError(StrictModel):
    """Generic error item in processing result."""

    item: str = Field(..., description="Item that could not be processed")
    error: str = Field(..., description="Error message")


class ProcessedResult(StrictModel):
    """Generic processing result."""

    success: list[ProcessedSuccess] = Field(
        default_factory=list, description="Successfully processed items"
    )
    errors: list[ProcessedError] = Field(
        default_factory=list, description="Processing errors"
    )
