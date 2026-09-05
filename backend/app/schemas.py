from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["guest", "manager"]
StayScene = Literal["business", "wellness", "family", "leisure"]
AgeGroup = Literal["18-25", "26-35", "36-50", "51+"]
Gender = Literal["male", "female", "other"]
LightPref = Literal["dark", "dim", "nightlight"]
SoundPref = Literal["silent", "white-noise", "soft-music"]
Firmness = Literal["soft", "medium", "firm"]
SleepIssue = Literal["insomnia", "light-sleeper", "snoring", "allergy"]
LightingLevel = Literal["off", "nightlight", "dim", "soft"]
CurtainLevel = Literal["closed", "half", "open"]
WhiteNoiseKind = Literal["off", "rain", "ocean", "fan", "music"]
SceneId = Literal["deep-aid", "business-quick", "wellness"]


class LoginIn(BaseModel):
    email: str
    password: str
    role: Role


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=4)
    nickname: str = Field(min_length=1)


class SessionOut(BaseModel):
    token: str
    email: str
    role: Role
    nickname: str


class DeviceSettings(BaseModel):
    acOn: bool
    targetTemp: float = Field(ge=16, le=32)
    targetHumidity: float = Field(ge=30, le=80)
    humidifierOn: bool
    lighting: LightingLevel
    curtain: CurtainLevel
    whiteNoise: WhiteNoiseKind
    fragranceOn: bool


class DevicePatch(BaseModel):
    acOn: bool | None = None
    targetTemp: float | None = Field(default=None, ge=16, le=32)
    targetHumidity: float | None = Field(default=None, ge=30, le=80)
    humidifierOn: bool | None = None
    lighting: LightingLevel | None = None
    curtain: CurtainLevel | None = None
    whiteNoise: WhiteNoiseKind | None = None
    fragranceOn: bool | None = None


class SleepPreferenceIn(BaseModel):
    nickname: str
    gender: Gender
    ageGroup: AgeGroup
    stayScene: StayScene
    bedtime: str
    wakeup: str
    preferredTemp: float = Field(ge=16, le=32)
    preferredHumidity: float = Field(ge=30, le=80)
    light: LightPref
    sound: SoundPref
    pillow: Firmness
    mattress: Firmness
    issues: list[SleepIssue] = []
    fragrance: str = ""
    bedtimeHabit: str = ""


class SleepPortrait(BaseModel):
    sceneId: SceneId
    sceneName: str
    sceneSummary: str
    reasons: list[str]
    settings: DeviceSettings
    tags: list[str]


class GuestOut(BaseModel):
    email: str
    nickname: str
    preference: SleepPreferenceIn | None
    portrait: SleepPortrait | None
    updatedAt: str | None


class EnsureGuestIn(BaseModel):
    email: str
    nickname: str


class BindGuestIn(BaseModel):
    email: str | None = None


class RoomEnv(BaseModel):
    temp: float
    humidity: float
    light: float
    noise: float


class RoomOut(BaseModel):
    id: str
    floor: int
    name: str
    occupied: bool
    guestEmail: str | None
    sceneApplied: bool
    env: RoomEnv
    devices: DeviceSettings
    history: list[float]


class HotelOverview(BaseModel):
    occupiedCount: int
    vacantCount: int
    avgTemp: float
    avgHumidity: float
    pendingAdaptCount: int


class EnvTrendPoint(BaseModel):
    temp: float
    humidity: float


class SimulationIn(BaseModel):
    running: bool
