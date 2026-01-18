from typing import List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl


class Toniebox(BaseModel):
    """
    Represents a Toniebox device.
    """

    accelerometer_enabled: bool = Field(alias="accelerometerEnabled")
    household: str
    household_id: str = Field(alias="householdId")
    id: str
    image_url: HttpUrl = Field(alias="imageUrl")
    front_image_url: HttpUrl = Field(alias="frontImageUrl")
    item_id: str = Field(alias="itemId")
    led_level: str = Field(alias="ledLevel")
    max_headphone_volume: int = Field(alias="maxHeadphoneVolume")
    max_volume: int = Field(alias="maxVolume")
    name: str
    tap_direction: str = Field(alias="tapDirection")
    timezone: Optional[str] = None
    features: List[str]
    settings_applied: bool = Field(alias="settingsApplied")
    mac_address: str = Field(alias="macAddress")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class User(BaseModel):
    """
    Represents a user with their details and flags.
    """

    # Fields from UserDetails
    accepted_terms_of_use: bool = Field(alias="acceptedTermsOfUse")
    any_public_content_tokens: bool = Field(alias="anyPublicContentTokens")
    country: str
    creative_tonie_shop_url: HttpUrl = Field(alias="creativeTonieShopUrl")
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
    profile_image: Optional[HttpUrl] = Field(alias="profileImage")
    tracking: bool
    unicode_locale: str = Field(alias="unicodeLocale")
    uuid: str
    # typename: str = Field(alias="__typename") # This will be duplicated, so we take one

    # Fields from UserFlags
    region: str
    can_buy_tunes: bool = Field(alias="canBuyTunes")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class Household(BaseModel):
    """
    Represents a household.
    """

    id: str
    name: str
    owner_name: str = Field(alias="ownerName")
    access: str
    foreign_creative_tonie_content: bool = Field(alias="foreignCreativeTonieContent")

    class Config:
        populate_by_name = True


# Models for UserToniesOverview
class Chapter(BaseModel):
    seconds: int
    title: str
    typename: str = Field(alias="__typename")


class ContentInfo(BaseModel):
    chapters: List[Chapter]
    seconds: int
    typename: str = Field(alias="__typename")


class Item(BaseModel):
    id: str
    content_info: ContentInfo = Field(alias="contentInfo")
    title: str
    tonie_shop_url: Optional[HttpUrl] = Field(alias="tonieShopUrl")
    thumbnail: Optional[HttpUrl]
    sales_id: Optional[str] = Field(alias="salesId")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class AssignedTonie(BaseModel):
    id: str
    image_url: HttpUrl = Field(alias="imageUrl")
    title: str
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class Tune(BaseModel):
    id: str
    assigned_tonies: List[AssignedTonie] = Field(alias="assignedTonies")
    item: Item
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class FreshnessCheck(BaseModel):
    manual: bool
    automatic: bool
    typename: str = Field(alias="__typename")


class Author(BaseModel):
    name: str
    typename: str = Field(alias="__typename")


class AssociatedContentToken(BaseModel):
    id: str
    token: str
    chapters: List[Chapter]
    thumbnail: Optional[HttpUrl]
    subtitle: Optional[str]
    title: str
    description: Optional[str]
    campaign: Optional[str]
    expired: bool
    authors: List[Author]
    typename: str = Field(alias="__typename")


class CreativeTonieChapter(BaseModel):
    id: str
    title: str
    file: Optional[HttpUrl]
    seconds: int
    transcoding: bool
    thumbnail: Optional[HttpUrl]
    type: Optional[str]
    typename: str = Field(alias="__typename")


class CreativeTonie(BaseModel):
    household: str
    id: str
    name: str
    image_url: HttpUrl = Field(alias="imageUrl")
    seconds_present: int = Field(alias="secondsPresent")
    seconds_remaining: int = Field(alias="secondsRemaining")
    live: bool
    private: bool
    associated_content_tokens: List[AssociatedContentToken] = Field(
        alias="associatedContentTokens"
    )
    chapters: List[CreativeTonieChapter]
    freshness_check: FreshnessCheck = Field(alias="freshnessCheck")
    tune: Optional[Tune] = None
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class Disc(BaseModel):
    id: str
    title: str
    disc_image_url: HttpUrl = Field(alias="discImageUrl")
    top_image_url: HttpUrl = Field(alias="topImageUrl")
    toniebox_image_url: HttpUrl = Field(alias="tonieboxImageUrl")
    household_id: str = Field(alias="householdId")
    cover_image_url: HttpUrl = Field(alias="coverImageUrl")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class Group(BaseModel):
    id: str
    name: str
    typename: str = Field(alias="__typename")


class Series(BaseModel):
    id: str
    name: str
    group: List[Group]


class ContentTonie(BaseModel):
    household: str
    id: str
    title: str
    seconds_present: int = Field(alias="secondsPresent")
    image_url: HttpUrl = Field(alias="imageUrl")
    cover_url: HttpUrl = Field(alias="coverUrl")
    language_unicode: str = Field(alias="languageUnicode")
    supported_languages: List[str] = Field(alias="supportedLanguages")
    series: Series
    tune: Tune
    freshness_check: FreshnessCheck = Field(alias="freshnessCheck")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class HouseholdWithTonies(Household):
    content_tonies: List[ContentTonie] = Field(alias="contentTonies")
    creative_tonies: List[CreativeTonie] = Field(alias="creativeTonies")
    discs: List[Disc]

    class Config:
        populate_by_name = True


# Models for GetChildren
class TonieboxInChild(BaseModel):
    id: str
    name: str
    image_url: HttpUrl = Field(alias="imageUrl")
    features: List[str]
    front_image_url: HttpUrl = Field(alias="frontImageUrl")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class Child(BaseModel):
    id: str
    name: str
    birth_date: Optional[str] = Field(alias="birthDate")
    gender: Optional[str]
    situations: List[str]
    tonieboxes: List[TonieboxInChild]
    taxonomies_preferences: List[str] = Field(alias="taxonomiesPreferences")
    taxonomies_avoid: List[str] = Field(alias="taxonomiesAvoid")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


# Models for GetHouseholdMembers
class CreativeTonieInPermission(BaseModel):
    id: str
    household_id: str = Field(alias="householdId")
    image_url: HttpUrl = Field(alias="imageUrl")
    name: str
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class Permission(BaseModel):
    creative_tonie: CreativeTonieInPermission = Field(alias="creativeTonie")
    permission: str
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


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
    profile_image: Optional[HttpUrl] = Field(alias="profileImage")
    permissions: List[Permission]
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class Invitation(BaseModel):
    email: str
    id: str
    itype: str
    typename: str = Field(alias="__typename")


class HouseholdMembersResponse(BaseModel):
    memberships: List[Member]
    invitations: List[Invitation]
    typename: str = Field(alias="__typename")


# Models for ContentTonieDetails
class TuneItemContentInfo(BaseModel):
    seconds: int
    typename: str = Field(alias="__typename")


class TuneItemSeriesGroup(BaseModel):
    id: str
    name: str
    typename: str = Field(alias="__typename")


class TuneItemSeries(BaseModel):
    id: str
    name: str
    group: TuneItemSeriesGroup
    slug: str
    typename: str = Field(alias="__typename")


class Genre(BaseModel):
    key: str
    typename: str = Field(alias="__typename")


class MyTuneAssignedTonie(BaseModel):
    id: str
    image_url: HttpUrl = Field(alias="imageUrl")
    cover_url: HttpUrl = Field(alias="coverUrl")
    title: str
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class MyTune(BaseModel):
    id: str
    assign_count_remaining: int = Field(alias="assignCountRemaining")
    assigned_tonies: List[MyTuneAssignedTonie] = Field(alias="assignedTonies")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class OwnedTune(BaseModel):
    description: str
    id: str
    tonie_shop_url: Optional[HttpUrl] = Field(alias="tonieShopUrl")
    thumbnail: Optional[HttpUrl]
    title: str
    exclusive: bool
    content_info: TuneItemContentInfo = Field(alias="contentInfo")
    series: TuneItemSeries
    genre: Genre
    sales_id: str = Field(alias="salesId")
    language_unicode: str = Field(alias="languageUnicode")
    min_age: int = Field(alias="minAge")
    my_tune: MyTune = Field(alias="myTune")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True


class ContentTonieDetailsChapter(BaseModel):
    title: str
    typename: str = Field(alias="__typename")


class ContentTonieDetailsSeriesGroup(BaseModel):
    id: str
    name: str
    thumbnail: Optional[HttpUrl]
    typename: str = Field(alias="__typename")


class ContentTonieDetailsSeries(BaseModel):
    id: str
    name: str
    group: List[ContentTonieDetailsSeriesGroup]
    typename: str = Field(alias="__typename")


class ContentTonieDetails(BaseModel):
    household: str
    id: str
    default_episode_id: str = Field(alias="defaultEpisodeId")
    title: str
    tune: Tune
    seconds_present: int = Field(alias="secondsPresent")
    image_url: HttpUrl = Field(alias="imageUrl")
    cover_url: HttpUrl = Field(alias="coverUrl")
    description: str
    lock: bool
    chapters: List[ContentTonieDetailsChapter]
    series: ContentTonieDetailsSeries
    owned_tunes: List[OwnedTune] = Field(alias="ownedTunes")
    typename: str = Field(alias="__typename")

    class Config:
        populate_by_name = True