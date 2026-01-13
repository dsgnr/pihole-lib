"""System resource models."""

from pydantic import Field

from pihole_lib.models.base import StrictModel


class MemoryStats(StrictModel):
    """Memory statistics (RAM or Swap)."""

    total: int = Field(..., description="Total memory in KB")
    free: int = Field(..., description="Free memory in KB")
    used: int = Field(..., description="Used memory in KB")
    percent_used: float = Field(
        ..., alias="%used", description="Percentage of memory used"
    )


class RAMStats(MemoryStats):
    """RAM statistics with available memory."""

    available: int = Field(..., description="Available memory in KB")


class Memory(StrictModel):
    """Combined RAM and swap memory information."""

    ram: RAMStats = Field(..., description="RAM information")
    swap: MemoryStats = Field(..., description="Swap information")


class CPULoad(StrictModel):
    """CPU load averages."""

    raw: list[float] = Field(..., description="Raw load averages (1, 5, 15 minutes)")
    percent: list[float] = Field(..., description="Load averages as percentages")


class CPUStats(StrictModel):
    """CPU statistics."""

    nprocs: int = Field(..., description="Number of CPU cores")
    percent_cpu: float = Field(..., alias="%cpu", description="CPU usage percentage")
    load: CPULoad = Field(..., description="Load average information")


class FTLResourceUsage(StrictModel):
    """FTL process resource usage."""

    percent_mem: float = Field(
        ..., alias="%mem", description="FTL memory usage percentage"
    )
    percent_cpu: float = Field(
        ..., alias="%cpu", description="FTL CPU usage percentage"
    )


class NetworkBytes(StrictModel):
    """Network byte count with unit."""

    value: float = Field(..., description="Byte value")
    unit: str = Field(..., description="Unit (e.g., 'K', 'M', 'G')")


class SystemDetails(StrictModel):
    """System resource details."""

    uptime: int = Field(..., description="System uptime in seconds")
    memory: Memory = Field(..., description="Memory information")
    procs: int = Field(..., description="Number of processes")
    cpu: CPUStats = Field(..., description="CPU information")
    ftl: FTLResourceUsage = Field(..., description="FTL resource usage")


class SystemInfo(StrictModel):
    """Pi-hole system information wrapper."""

    system: SystemDetails = Field(..., description="System details")
