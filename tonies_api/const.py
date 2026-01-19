AUTH_BASE_URL = "https://login.tonies.com"
AUTH_PATH = "/auth/realms/tonies/protocol/openid-connect/auth"
TOKEN_PATH = "/auth/realms/tonies/protocol/openid-connect/token"
CLIENT_ID = "tonie-studio"
SCOPE = "openid profile email"
REDIRECT_URI = "com.tonies.app:/oauthredirect"
API_BASE_URL = "https://api.tonie.cloud/v2"
GRAPHQL_URL = "https://api.tonie.cloud/v2/graphql"
WEBSOCKET_URL = "wss://ici.tonie.cloud/"

OAUTH_URL = (
    f"{AUTH_BASE_URL}{AUTH_PATH}"
    f"?client_id={CLIENT_ID}"
    "&kc_locale=en-US"
    f"&redirect_uri={REDIRECT_URI}"
    "&response_type=code"
    f"&scope={SCOPE}"
    "&webview=app"
    "&utm_source=app"
    "&cookieConsent=0"
)

GET_HOUSEHOLDS_BOXES_QUERY = {
    "operationName": "GetHouseholdsBoxes",
    "variables": {},
    "query": """query GetHouseholdsBoxes {
      households {
        id
        name
        ownerName
        access
        tonieboxes {
          accelerometerEnabled
          household: householdId
          householdId
          id
          imageUrl
          frontImageUrl
          itemId
          ledLevel
          lightringBrightness
          bedtimeLightringBrightness
          bedtimeLightringColor
          bedtimeMaxVolume
          bedtimeMaxHeadphoneVolume   
          maxHeadphoneVolume
          maxVolume
          name
          tapDirection
          timezone
          features
          settingsApplied
          macAddress
          bedtimeSchedules { 
            id
            name
            enabled
            sleepTime
            wakeupTime
            alarmEnabled
            alarmMorningLight
            alarmTone
            alarmToneLabel
            alarmVolume
            days
          }
        }
      }
    }""",
}

GET_USER_DETAILS_QUERY = {
    "operationName": "GetUserDetails",
    "variables": {},
    "query": """query GetUserDetails {
      me {
        acceptedTermsOfUse
        anyPublicContentTokens
        country
        creativeTonieShopUrl
        email
        firstName
        hasAnyContentTonies
        hasAnyCreativeTonies
        hasTblToniebox: hasAnyTonieboxes(generations: ["classic", "rosered"])
        hasTngToniebox: hasAnyTonieboxes(generation: "tng")
        hasAnyDiscs
        isBetaTester
        isEduUser
        lastName
        locale
        notificationCount
        ownsTunes
        profileImage
        tracking
        unicodeLocale
        uuid
        __typename
      }
      flags {
        region: contentRegion
        canBuyTunes
        __typename
      }
    }""",
}

GET_HOUSEHOLDS_QUERY = {
    "query": """query GetHouseHolds {
      households {
        id
        name
        ownerName
        access
        foreignCreativeTonieContent
      }
    }""",
    "operationName": "GetHouseHolds",
}

USER_TONIES_OVERVIEW_QUERY = {
    "operationName": "UserToniesOverview",
    "variables": {},
    "query": """
        fragment CommonTune on TuneType {
          id
          assignedTonies {
            id
            imageUrl
            title
            __typename
          }
          item {
            id
            contentInfo {
              chapters {
                seconds
                title
                __typename
              }
              seconds
              __typename
            }
            title
            tonieShopUrl
            thumbnail
            salesId
            __typename
          }
          __typename
        }

        fragment CommonFreshnessCheck on FreshnessCheckQuery {
          manual
          automatic
          __typename
        }

        fragment CommonCreativeTonie on CreativeTonieQuery {
          household: householdId
          id
          name
          imageUrl
          secondsPresent
          secondsRemaining
          live
          private
          associatedContentTokens {
            id
            token
            chapters {
              seconds
              title
              __typename
            }
            thumbnail
            subtitle
            title
            description
            campaign
            expired
            authors {
              name
              __typename
            }
            __typename
          }
          chapters {
            id
            title
            file
            seconds
            transcoding
            thumbnail
            type
            __typename
          }
          freshnessCheck {
            ...CommonFreshnessCheck
            __typename
          }
          __typename
        }

        fragment CommonDisc on DiscQuery {
          id
          title
          discImageUrl
          topImageUrl
          tonieboxImageUrl
          householdId
          coverImageUrl
          __typename
        }

        query UserToniesOverview {
          households {
            id
            name
            ownerName
            access
            foreignCreativeTonieContent
            contentTonies {
              household: householdId
              id
              title
              secondsPresent
              imageUrl
              coverUrl
              languageUnicode
              supportedLanguages
              series {
                id
                name
                group(all: true) {
                  id
                  name
                  __typename
                }
                __typename
              }
              tune {
                ...CommonTune
                __typename
              }
              freshnessCheck {
                manual
                automatic
                __typename
              }
              __typename
            }
            creativeTonies {
              ...CommonCreativeTonie
              tune {
                ...CommonTune
                __typename
              }
              __typename
            }
            discs {
              ...CommonDisc
              __typename
            }
            __typename
          }
        }
    """,
}

GET_CHILDREN_QUERY = """
    query GetChildren($id: String!, $childId: String) {
      households(id: $id) {
        children(id: $childId) {
          id
          name
          birthDate
          gender
          situations
          tonieboxes {
            id
            name
            imageUrl
            features
            frontImageUrl
            __typename
          }
          taxonomiesPreferences
          taxonomiesAvoid
          __typename
        }
        __typename
      }
    }
"""

GET_HOUSEHOLD_MEMBERS_QUERY = """
    query GetHouseholdMembers($householdId: String!) {
      households(id: $householdId) {
        memberships {
          canDelete
          canEdit
          displayName
          email
          firstName
          id
          isSelf
          lastName
          mtype
          profileImage
          permissions {
            creativeTonie {
              id
              householdId
              imageUrl
              name
              __typename
            }
            permission
            __typename
          }
          __typename
        }
        invitations {
          email
          id
          itype
          __typename
        }
        __typename
      }
    }
"""

CONTENT_TONIE_DETAILS_QUERY = """
    fragment CommonTune on TuneType {
      id
      assignedTonies {
        id
        imageUrl
        title
        __typename
      }
      item {
        id
        contentInfo {
          chapters {
            seconds
            title
            __typename
          }
          seconds
          __typename
        }
        title
        tonieShopUrl
        thumbnail
        salesId
        __typename
      }
      __typename
    }

    fragment CommonTuneItem on TunesItemType {
      description
      id
      tonieShopUrl
      thumbnail
      title
      exclusive
      contentInfo {
        seconds
        __typename
      }
      series {
        id
        name
        group {
          id
          name
          __typename
        }
        slug
        __typename
      }
      genre {
        key
        __typename
      }
      salesId
      languageUnicode
      minAge
      __typename
    }

    query ContentTonieDetails($householdId: String!, $tonieId: String!) {
      households(id: $householdId) {
        contentTonies(id: $tonieId) {
          household: householdId
          id
          defaultEpisodeId
          title
          tune {
            ...CommonTune
            __typename
          }
          secondsPresent
          imageUrl
          coverUrl
          description
          lock
          chapters {
            title: name
            __typename
          }
          series {
            id
            name
            group(all: true) {
              id
              name
              thumbnail
              __typename
            }
            __typename
          }
          ownedTunes: suitableTunesItems(myTuneStatus: "owned", count: 20) {
            ...CommonTuneItem
            series {
              id
              name
              group {
                id
                name
                __typename
              }
              __typename
            }
            myTune {
              id
              assignCountRemaining
              assignedTonies {
                id
                imageUrl
                coverUrl
                title
                __typename
              }
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
    }
"""
