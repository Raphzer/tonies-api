from __future__ import annotations

from typing import List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class Toniebox(BaseModel):
    """
    Represents a Toniebox device.
    """

    accelerometer_enabled: bool = Field(alias="accelerometerEnabled")
    household: Optional[str] = None
    household_id: str = Field(alias="householdId")
    id: str
    image_url: str = Field(alias="imageUrl")
    front_image_url: str = Field(alias="frontImageUrl")
    item_id: str = Field(alias="itemId")
    led_level: str = Field(alias="ledLevel")
    lightring_brightness: Optional[int] = Field(alias="lightringBrightness")
    bedtime_lightring_brightness: Optional[int] = Field(alias="bedtimeLightringBrightness")
    bedtime_lightring_color: Optional[str] = Field(alias="bedtimeLightringColor")    
    max_headphone_volume: int = Field(alias="maxHeadphoneVolume")
    max_volume: int = Field(alias="maxVolume")
    bedtime_max_volume: Optional[int] = Field(alias="bedtimeMaxVolume")
    bedtime_max_headphone_volume: Optional[int] = Field(alias="bedtimeMaxHeadphoneVolume")
    name: str
    tap_direction: str = Field(alias="tapDirection")
    timezone: Optional[str] = None
    features: List[str]
    settings_applied: bool = Field(alias="settingsApplied")
    mac_address: str = Field(alias="macAddress")
    bedtime_schedules: List[BetTimeSchedules] = Field(alias="bedtimeSchedules") 
    model_config = ConfigDict(populate_by_name=True)




class BetTimeSchedules(BaseModel):
    id: str
    name: str
    enabled: bool
    sleep_time: str = Field(alias="sleepTime")
    wakeup_time: str = Field(alias="wakeupTime")
    alarm_enabled: bool = Field(alias="alarmEnabled")
    alarm_morning_light: bool = Field(alias="alarmMorningLight")
    alarm_tone: str = Field(alias="alarmTone")
    alarm_tone_label: str = Field(alias="alarmToneLabel")
    alarm_volume: int = Field(alias="alarmVolume")
    days: List[str]




class User(BaseModel):
    """
    Represents a user with their details and flags.
    """

    # Fields from UserDetails
    accepted_terms_of_use: bool = Field(alias="acceptedTermsOfUse")
    any_public_content_tokens: bool = Field(alias="anyPublicContentTokens")
    country: str
    creative_tonie_shop_url: str = Field(alias="creativeTonieShopUrl")
    email: str
    first_name: str = Field(alias="firstName")
    has_any_content_tonies: bool = Field(alias="hasAnyContentTonies")
    has_any_creative_tonies: bool = Field(alias="hasAnyCreativeTonies")
    has_tbl_toniebox: bool = Field(alias="hasTblToniebox")
    has_tng_toniebox: bool = Field(alias="hasTngToniebox")
    has_any_discs: bool = Field(alias="hasAnyDiscs")
    is_beta_tester: bool = Field(alias="isBetaTester")
    is_edu_user: bool = Field(alias="isEduUser")
    last_name: str = Field(alias="lastName")
    locale: str
    notification_count: int = Field(alias="notificationCount")
    owns_tunes: bool = Field(alias="ownsTunes")
    profile_image: str = Field(alias="profileImage")
    tracking: bool
    unicode_locale: str = Field(alias="unicodeLocale")
    uuid: str

    # Fields from UserFlags
    region: str
    can_buy_tunes: bool = Field(alias="canBuyTunes")

    model_config = ConfigDict(populate_by_name=True)



class Household(BaseModel):
    """
    Represents a household.
    """

    id: str
    name: str
    owner_name: str = Field(alias="ownerName")
    access: str
    foreign_creative_tonie_content: bool = Field(alias="foreignCreativeTonieContent")
    model_config = ConfigDict(populate_by_name=True)



# Models for UserToniesOverview
class Chapter(BaseModel):
    seconds: float
    title: str


class ContentInfo(BaseModel):
    chapters: List[Chapter]
    seconds: float


class Item(BaseModel):
    id: str
    content_info: ContentInfo = Field(alias="contentInfo")
    title: str
    tonie_shop_url: Optional[str] = Field(alias="tonieShopUrl")
    thumbnail: Optional[str]
    sales_id: Optional[str] = Field(alias="salesId")
    model_config = ConfigDict(populate_by_name=True)



class AssignedTonie(BaseModel):
    id: str
    image_url: str = Field(alias="imageUrl")
    title: str
    model_config = ConfigDict(populate_by_name=True)



class Tune(BaseModel):
    id: str
    assigned_tonies: List[AssignedTonie] = Field(alias="assignedTonies")
    item: Item
    model_config = ConfigDict(populate_by_name=True)



class FreshnessCheck(BaseModel):
    manual: bool
    automatic: bool



class Author(BaseModel):
    name: str



class AssociatedContentToken(BaseModel):
    id: str
    token: str
    chapters: List[Chapter]
    thumbnail: Optional[str]
    subtitle: Optional[str]
    title: str
    description: Optional[str]
    campaign: Optional[str]
    expired: Optional[bool]
    authors: List[Author]



class CreativeTonieChapter(BaseModel):
    id: str
    title: str
    file: Optional[str]
    seconds: float
    transcoding: bool
    thumbnail: Optional[str]
    type: Optional[str]



class CreativeTonie(BaseModel):
    household: str
    id: str
    name: str
    image_url: str = Field(alias="imageUrl")
    seconds_present: float = Field(alias="secondsPresent")
    seconds_remaining: float = Field(alias="secondsRemaining")
    live: bool
    private: bool
    associated_content_tokens: List[AssociatedContentToken] = Field(
        alias="associatedContentTokens"
    )
    chapters: List[CreativeTonieChapter]
    freshness_check: FreshnessCheck = Field(alias="freshnessCheck")
    tune: Optional[Tune] = None


    model_config = ConfigDict(populate_by_name=True)



class Disc(BaseModel):
    id: str
    title: str
    disc_image_url: str = Field(alias="discImageUrl")
    top_image_url: str = Field(alias="topImageUrl")
    toniebox_image_url: str = Field(alias="tonieboxImageUrl")
    household_id: str = Field(alias="householdId")
    cover_image_url: str = Field(alias="coverImageUrl")

    model_config = ConfigDict(populate_by_name=True)



class Group(BaseModel):
    id: str
    name: str



class Series(BaseModel):
    id: str
    name: str
    group: Group


class ContentTonie(BaseModel):
    household: str
    id: str
    title: str
    seconds_present: float = Field(alias="secondsPresent")
    image_url: str = Field(alias="imageUrl")
    cover_url: str = Field(alias="coverUrl")
    language_unicode: str = Field(alias="languageUnicode")
    supported_languages: Optional[List[str]] = Field(alias="supportedLanguages")
    series: Series
    tune: Optional[Tune]
    freshness_check: FreshnessCheck = Field(alias="freshnessCheck")

    model_config = ConfigDict(populate_by_name=True)



class HouseholdWithTonies(Household):
    content_tonies: List[ContentTonie] = Field(alias="contentTonies")
    creative_tonies: List[CreativeTonie] = Field(alias="creativeTonies")
    discs: List[Disc]


# Models for GetChildren
class TonieboxInChild(BaseModel):
    id: str
    name: str
    image_url: str = Field(alias="imageUrl")
    features: List[str]
    front_image_url: str = Field(alias="frontImageUrl")

    model_config = ConfigDict(populate_by_name=True)



class Child(BaseModel):
    id: str
    name: str
    birth_date: Optional[str] = Field(alias="birthDate")
    gender: Optional[str]
    situations: Optional[List[str]]
    tonieboxes: Optional[List[TonieboxInChild]]
    taxonomies_preferences: Optional[List[str]] = Field(alias="taxonomiesPreferences")
    taxonomies_avoid: Optional[List[str]] = Field(alias="taxonomiesAvoid")

    model_config = ConfigDict(populate_by_name=True)



# Models for GetHouseholdMembers
class CreativeTonieInPermission(BaseModel):
    id: str
    household_id: str = Field(alias="householdId")
    image_url: str = Field(alias="imageUrl")
    name: str

    model_config = ConfigDict(populate_by_name=True)



class Permission(BaseModel):
    creative_tonie: CreativeTonieInPermission = Field(alias="creativeTonie")
    permission: str

    model_config = ConfigDict(populate_by_name=True)



class Member(BaseModel):
    can_delete: bool = Field(alias="canDelete")
    can_edit: bool = Field(alias="canEdit")
    display_name: str = Field(alias="displayName")
    email: str
    first_name: str = Field(alias="firstName")
    id: str
    is_self: bool = Field(alias="isSelf")
    last_name: str = Field(alias="lastName")
    mtype: str
    profile_image: Optional[str] = Field(alias="profileImage")
    permissions: List[Permission]

    model_config = ConfigDict(populate_by_name=True)



class Invitation(BaseModel):
    email: str
    id: str
    itype: str



class HouseholdMembersResponse(BaseModel):
    memberships: List[Member]
    invitations: List[Invitation]



# Models for ContentTonieDetails
class TuneItemContentInfo(BaseModel):
    seconds: float



class TuneItemSeriesGroup(BaseModel):
    id: str
    name: str



class TuneItemSeries(BaseModel):
    id: str
    name: str
    group: TuneItemSeriesGroup
    slug: str



class Genre(BaseModel):
    key: str



class MyTuneAssignedTonie(BaseModel):
    id: str
    image_url: str = Field(alias="imageUrl")
    cover_url: str = Field(alias="coverUrl")
    title: str

    model_config = ConfigDict(populate_by_name=True)



class MyTune(BaseModel):
    id: str
    assign_count_remaining: int = Field(alias="assignCountRemaining")
    assigned_tonies: List[MyTuneAssignedTonie] = Field(alias="assignedTonies")

    model_config = ConfigDict(populate_by_name=True)



class OwnedTune(BaseModel):
    description: str
    id: str
    tonie_shop_url: Optional[str] = Field(alias="tonieShopUrl")
    thumbnail: Optional[str]
    title: str
    exclusive: bool
    content_info: TuneItemContentInfo = Field(alias="contentInfo")
    series: TuneItemSeries
    genre: Genre
    sales_id: str = Field(alias="salesId")
    language_unicode: str = Field(alias="languageUnicode")
    min_age: int = Field(alias="minAge")
    my_tune: MyTune = Field(alias="myTune")
    model_config = ConfigDict(populate_by_name=True)



class ContentTonieDetailsChapter(BaseModel):
    title: str



class ContentTonieDetailsSeriesGroup(BaseModel):
    id: str
    name: str
    thumbnail: Optional[str]



class ContentTonieDetailsSeries(BaseModel):
    id: str
    name: str
    group: ContentTonieDetailsSeriesGroup



class ContentTonieDetails(BaseModel):
    household: str
    id: str
    default_episode_id: str = Field(alias="defaultEpisodeId")
    title: str
    tune: Optional[Tune]
    seconds_present: float = Field(alias="secondsPresent")
    image_url: str = Field(alias="imageUrl")
    cover_url: str = Field(alias="coverUrl")
    description: str
    lock: bool
    chapters: List[ContentTonieDetailsChapter]
    series: ContentTonieDetailsSeries
    owned_tunes: List[OwnedTune] = Field(alias="ownedTunes")

    model_config = ConfigDict(populate_by_name=True)
