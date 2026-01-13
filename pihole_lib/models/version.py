"""Version models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel, TimedResponse


class VersionLocal(StrictModel):
    """Local version information."""

    version: str = Field(..., description="Version string")
    branch: str | None = Field(None, description="Git branch")
    hash: str = Field(..., description="Git commit hash")
    date: str | None = Field(None, description="Build date")


class VersionRemote(StrictModel):
    """Remote version information."""

    version: str | None = Field(None, description="Version string")
    hash: str | None = Field(None, description="Git commit hash")


class ComponentVersion(StrictModel):
    """Component version information."""

    local: VersionLocal = Field(..., description="Local version information")
    remote: VersionRemote = Field(..., description="Remote version information")


class DockerVersion(StrictModel):
    """Docker version information."""

    local: str | None = Field(None, description="Local Docker version")
    remote: str | None = Field(None, description="Remote Docker version")


class VersionDetails(StrictModel):
    """Pi-hole version details for all components."""

    core: ComponentVersion = Field(..., description="Pi-hole core version information")
    web: ComponentVersion = Field(
        ..., description="Pi-hole web interface version information"
    )
    ftl: ComponentVersion = Field(..., description="FTL version information")
    docker: DockerVersion = Field(..., description="Docker image version information")


class VersionInfo(TimedResponse):
    """Pi-hole version information response."""

    version: VersionDetails = Field(
        ..., description="Version details for all components"
    )
