import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pyatlan.client.atlan import AtlanClient
from pyatlan.model.search import DSL, Bool, Term, Match, IndexSearchRequest, FluentSearch
from pyatlan.model.assets import AtlasGlossaryTerm, GlossaryTerm
import requests

load_dotenv()

class AtlanSDKClient:
    def __init__(self):
        # Get configuration from environment variables
        self.base_url = os.getenv("ATLAN_BASE_URL", "https://home.atlan.com")
        self.api_token = os.getenv("ATLAN_API_TOKEN")
        
        # Initialize Atlan client
        self.client = AtlanClient(
            base_url=self.base_url,
            api_key=self.api_token
        )
        
    def test_connection(self) -> bool:
        """Test Atlan SDK connection"""
        try:
            # Try to get current user info as a connection test
            user = self.client.get_current_user()
            print(f"✅ Atlan SDK connection successful - User: {user.username}")
            return True
        except Exception as e:
            print(f"❌ Atlan SDK connection test failed: {e}")
            return False
    
    def find_assets_with_term(self, term_guid: str, term_name: str = None) -> List[Dict[str, Any]]:
        """Find all assets linked to a glossary term using proper Atlan SDK methods"""
        print(f"🔍 Finding assets linked to term: {term_name or term_guid}")
        
        all_assets = []
        
        try:
            # Strategy 1: Use Atlan's relationship API to find assets with this term in their meanings
            print("Trying relationship-based search using Atlan SDK...")
            
            # Search for assets that have this term in their meanings
            search_body = {
                "dsl": {
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"__state": "ACTIVE"}},
                                {"nested": {
                                    "path": "meanings",
                                    "query": {
                                        "term": {"meanings.termGuid.keyword": term_guid}
                                    }
                                }}
                            ]
                        }
                    }
                },
                "attributes": [
                    "guid", "typeName", "name", "qualifiedName", "description", 
                    "userDescription", "certificateStatus", "ownerUsers", "ownerGroups",
                    "assetTags", "connectionName", "connectorName", "viewScore",
                    "popularityScore", "starredCount", "displayName"
                ],
                "size": 50
            }
            
            response = requests.post(
                f"{self.base_url}/api/meta/search/indexsearch",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                },
                json=search_body
            )
            
            if response.status_code == 200:
                data = response.json()
                if "entities" in data and data["entities"]:
                    print(f"✅ Relationship search found {len(data['entities'])} assets")
                    assets = self._process_api_entities(data["entities"])
                    all_assets.extend(assets)
                else:
                    print("❌ No assets found in relationship search")
            else:
                print(f"❌ Relationship search failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Relationship search error: {e}")
        
        # Strategy 2: If no assets found, try searching by term name in asset descriptions
        if not all_assets and term_name:
            print(f"Trying fallback search by term name: {term_name}")
            try:
                # Search for assets that mention the term name in their description or name
                search_body = {
                    "dsl": {
                        "query": {
                            "bool": {
                                "must": [
                                    {"term": {"__state": "ACTIVE"}},
                                    {"bool": {
                                        "should": [
                                            {"wildcard": {"name": f"*{term_name.lower()}*"}},
                                            {"wildcard": {"displayName": f"*{term_name.lower()}*"}},
                                            {"wildcard": {"description": f"*{term_name.lower()}*"}},
                                            {"wildcard": {"userDescription": f"*{term_name.lower()}*"}}
                                        ]
                                    }}
                                ]
                            }
                        }
                    },
                    "attributes": [
                        "guid", "typeName", "name", "qualifiedName", "description", 
                        "userDescription", "certificateStatus", "ownerUsers", "ownerGroups",
                        "assetTags", "connectionName", "connectorName", "viewScore",
                        "popularityScore", "starredCount", "displayName"
                    ],
                    "size": 30
                }
                
                response = requests.post(
                    f"{self.base_url}/api/meta/search/indexsearch",
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Content-Type": "application/json"
                    },
                    json=search_body
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "entities" in data and data["entities"]:
                        print(f"✅ Fallback search found {len(data['entities'])} assets")
                        assets = self._process_api_entities(data["entities"])
                        all_assets.extend(assets)
                    else:
                        print("❌ No assets found in fallback search")
                else:
                    print(f"❌ Fallback search failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Fallback search error: {e}")
        
        # Remove duplicates and limit results
        unique_assets = []
        seen_guids = set()
        for asset in all_assets:
            if asset.get("guid") and asset["guid"] not in seen_guids:
                unique_assets.append(asset)
                seen_guids.add(asset["guid"])
        
        # Limit to 40 assets total
        final_assets = unique_assets[:40]
        print(f"🎯 Final result: {len(final_assets)} unique assets found")
        
        return final_assets
    
    def _process_sdk_assets(self, assets: List) -> List[Dict[str, Any]]:
        """Process assets returned by Atlan SDK into standardized format"""
        processed_assets = []
        
        for asset in assets:
            try:
                processed_asset = {
                    "guid": getattr(asset, 'guid', None),
                    "name": getattr(asset, 'name', None),
                    "typeName": getattr(asset, 'type_name', None),
                    "qualifiedName": getattr(asset, 'qualified_name', None),
                    "description": getattr(asset, 'description', None),
                    "userDescription": getattr(asset, 'user_description', None),
                    "certificateStatus": getattr(asset, 'certificate_status', None),
                    "ownerUsers": getattr(asset, 'owner_users', []),
                    "ownerGroups": getattr(asset, 'owner_groups', []),
                    "assetTags": getattr(asset, 'asset_tags', []),
                    "termType": getattr(asset, 'term_type', None),
                    "popularityScore": getattr(asset, 'popularity_score', None),
                    "starredCount": getattr(asset, 'starred_count', None),
                    "displayName": getattr(asset, 'display_name', None),
                    "abbreviation": getattr(asset, 'abbreviation', None),
                    "examples": getattr(asset, 'examples', None),
                    "readme": getattr(asset, 'readme', None),
                    "connectionName": getattr(asset, 'connection_name', None),
                    "connectorName": getattr(asset, 'connector_name', None),
                    "databaseName": getattr(asset, 'database_name', None),
                    "schemaName": getattr(asset, 'schema_name', None),
                    "announcementTitle": getattr(asset, 'announcement_title', None),
                    "announcementMessage": getattr(asset, 'announcement_message', None),
                    "information": getattr(asset, 'information', None),
                    "summary": getattr(asset, 'summary', None),
                    "notes": getattr(asset, 'notes', None),
                    "viewScore": getattr(asset, 'view_score', None)
                }
                
                # Remove None values
                processed_asset = {k: v for k, v in processed_asset.items() if v is not None}
                processed_assets.append(processed_asset)
                
            except Exception as e:
                print(f"❌ Error processing asset: {e}")
                continue
        
        return processed_assets
    
    def _fallback_api_search(self, term_guid: str, term_name: str = None) -> List[Dict[str, Any]]:
        """Fallback to direct API search if SDK methods fail"""
        print("🔄 Using fallback API search...")
        
        try:
            # Search for assets that have this term in their meanings
            search_body = {
                "dsl": {
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"__state": "ACTIVE"}}
                            ],
                            "should": [
                                {"nested": {
                                    "path": "meanings",
                                    "query": {
                                        "bool": {
                                            "must": [
                                                {"term": {"meanings.termGuid": term_guid}}
                                            ]
                                        }
                                    }
                                }},
                                {"term": {"meanings.termGuid.keyword": term_guid}}
                            ],
                            "minimum_should_match": 1
                        }
                    }
                },
                "attributes": ["name", "typeName", "qualifiedName", "guid", "description", 
                              "userDescription", "certificateStatus", "ownerUsers", 
                              "ownerGroups", "assetTags", "qualifiedName", "termType", 
                              "popularityScore", "starredCount", "displayName", "abbreviation", 
                              "examples", "readme", "connectionName", "connectorName", 
                              "databaseName", "schemaName", "announcementTitle", 
                              "announcementMessage", "information", "summary", "notes", "viewScore"],
                "size": 40
            }
            
            response = requests.post(
                f"{self.base_url}/api/meta/search/indexsearch",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                },
                json=search_body
            )
            
            if response.status_code == 200:
                data = response.json()
                entities = data.get('entities', [])
                
                if entities:
                    print(f"✅ Fallback API search found {len(entities)} assets")
                    return self._process_api_entities(entities)
                else:
                    print("❌ Fallback API search found 0 assets")
            else:
                print(f"❌ Fallback API search failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error in fallback API search: {e}")
        
        return []
    
    def _search_cac_related_assets(self) -> List[Dict[str, Any]]:
        """This method is deprecated - use find_assets_with_term instead"""
        print("⚠️  _search_cac_related_assets is deprecated - use find_assets_with_term instead")
        return []
    
    def _search_assets_by_term_name(self, term_name: str) -> List[Dict[str, Any]]:
        """This method is deprecated - use find_assets_with_term instead"""
        print("⚠️  _search_assets_by_term_name is deprecated - use find_assets_with_term instead")
        return []
    
    def _search_assets_by_related_terms(self, term_name: str) -> List[Dict[str, Any]]:
        """This method is deprecated - use find_assets_with_term instead"""
        print("⚠️  _search_assets_by_related_terms is deprecated - use find_assets_with_term instead")
        return []
    
    def _process_api_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process entities from direct API response"""
        processed = []
        for entity in entities:
            if entity:
                result = self._extract_asset_attributes(entity)
                if result:
                    processed.append(result)
        return processed
    
    def _process_entities(self, entities: List) -> List[Dict[str, Any]]:
        """Process and format entities from SDK response"""
        processed = []
        for entity in entities:
            entity_dict = {}
            
            # Basic fields - extract actual values
            entity_dict["name"] = getattr(entity, 'name', 'Unknown')
            entity_dict["typeName"] = getattr(entity, 'type_name', 'Unknown')
            entity_dict["qualifiedName"] = getattr(entity, 'qualified_name', '')
            entity_dict["guid"] = getattr(entity, 'guid', '')
            
            # Debug: Let's see what we actually have
            print(f"DEBUG: Processing entity: {entity_dict['name']}")
            print(f"DEBUG: Entity type: {type(entity)}")
            print(f"DEBUG: Entity dir: {[attr for attr in dir(entity) if not attr.startswith('_')][:20]}...")
            
            # Try to get all attributes directly from the entity object
            # Atlan objects might have attributes as direct properties or as nested objects
            
            # Description fields - try direct access first
            description = None
            if hasattr(entity, 'description'):
                desc_obj = getattr(entity, 'description')
                print(f"DEBUG: description object: {desc_obj} (type: {type(desc_obj)})")
                if desc_obj:
                    if hasattr(desc_obj, 'value'):
                        description = desc_obj.value
                    elif hasattr(desc_obj, 'text'):
                        description = desc_obj.text
                    elif hasattr(desc_obj, 'content'):
                        description = desc_obj.content
                    elif isinstance(desc_obj, str):
                        description = desc_obj
                    else:
                        description = str(desc_obj)
            entity_dict["description"] = description
            
            user_description = None
            if hasattr(entity, 'user_description'):
                user_desc_obj = getattr(entity, 'user_description')
                print(f"DEBUG: user_description object: {user_desc_obj} (type: {type(user_desc_obj)})")
                if user_desc_obj:
                    if hasattr(user_desc_obj, 'value'):
                        user_description = user_desc_obj.value
                    elif hasattr(user_desc_obj, 'text'):
                        user_description = user_desc_obj.text
                    elif hasattr(user_desc_obj, 'content'):
                        user_description = user_desc_obj.content
                    elif isinstance(user_desc_obj, str):
                        user_description = user_desc_obj
                    else:
                        user_description = str(user_desc_obj)
            entity_dict["userDescription"] = user_description
            
            long_description = None
            if hasattr(entity, 'long_description'):
                long_desc_obj = getattr(entity, 'long_description')
                if long_desc_obj:
                    if hasattr(long_desc_obj, 'value'):
                        long_description = long_desc_obj.value
                    elif hasattr(long_desc_obj, 'text'):
                        long_description = long_desc_obj.text
                    elif hasattr(long_desc_obj, 'content'):
                        long_description = long_desc_obj.content
                    elif isinstance(long_desc_obj, str):
                        long_description = long_desc_obj
                    else:
                        long_description = str(long_desc_obj)
            entity_dict["longDescription"] = long_description
            
            # Certificate status
            cert_status = None
            if hasattr(entity, 'certificate_status'):
                cert_obj = getattr(entity, 'certificate_status')
                print(f"DEBUG: certificate_status object: {cert_obj} (type: {type(cert_obj)})")
                if cert_obj:
                    if hasattr(cert_obj, 'value'):
                        cert_status = cert_obj.value
                    elif hasattr(cert_obj, 'name'):
                        cert_status = cert_obj.name
                    elif isinstance(cert_obj, str):
                        cert_status = cert_obj
                    else:
                        cert_status = str(cert_obj)
            entity_dict["certificateStatus"] = cert_status
            
            # Owners - extract actual names
            owner_users = []
            if hasattr(entity, 'owner_users'):
                owners_obj = getattr(entity, 'owner_users')
                print(f"DEBUG: owner_users object: {owners_obj} (type: {type(owners_obj)})")
                if owners_obj:
                    if isinstance(owners_obj, list):
                        for owner in owners_obj:
                            if hasattr(owner, 'name'):
                                owner_users.append(owner.name)
                            elif hasattr(owner, 'value'):
                                owner_users.append(owner.value)
                            elif hasattr(owner, 'display_name'):
                                owner_users.append(owner.display_name)
                            elif isinstance(owner, str):
                                owner_users.append(owner)
                            else:
                                owner_users.append(str(owner))
                    else:
                        # Single owner object
                        if hasattr(owners_obj, 'name'):
                            owner_users.append(owners_obj.name)
                        elif hasattr(owners_obj, 'value'):
                            owner_users.append(owners_obj.value)
                        elif isinstance(owners_obj, str):
                            owner_users.append(owners_obj)
                        else:
                            owner_users.append(str(owners_obj))
            entity_dict["ownerUsers"] = owner_users
            
            owner_groups = []
            if hasattr(entity, 'owner_groups'):
                groups_obj = getattr(entity, 'owner_groups')
                if groups_obj:
                    if isinstance(groups_obj, list):
                        for group in groups_obj:
                            if hasattr(group, 'name'):
                                owner_groups.append(group.name)
                            elif hasattr(group, 'value'):
                                owner_groups.append(group.value)
                            elif hasattr(group, 'display_name'):
                                owner_groups.append(group.display_name)
                            elif isinstance(group, str):
                                owner_groups.append(group)
                            else:
                                owner_groups.append(str(group))
                    else:
                        # Single group object
                        if hasattr(groups_obj, 'name'):
                            owner_groups.append(groups_obj.name)
                        elif hasattr(groups_obj, 'value'):
                            owner_groups.append(groups_obj.value)
                        elif isinstance(groups_obj, str):
                            owner_groups.append(groups_obj)
                        else:
                            owner_groups.append(str(groups_obj))
            entity_dict["ownerGroups"] = owner_groups
            
            # Score and popularity
            popularity_score = None
            if hasattr(entity, 'popularity_score'):
                score_obj = getattr(entity, 'popularity_score')
                if score_obj:
                    if hasattr(score_obj, 'value'):
                        popularity_score = score_obj.value
                    elif isinstance(score_obj, (int, float)):
                        popularity_score = score_obj
                    else:
                        popularity_score = score_obj
            entity_dict["popularityScore"] = popularity_score
            
            starred_count = None
            if hasattr(entity, 'starred_count'):
                starred_obj = getattr(entity, 'starred_count')
                if starred_obj:
                    if hasattr(starred_obj, 'value'):
                        starred_count = starred_obj.value
                    elif isinstance(starred_obj, (int, float)):
                        starred_count = starred_obj
                    else:
                        starred_count = starred_obj
            entity_dict["starredCount"] = starred_count
            
            # Categories and tags
            asset_tags = []
            if hasattr(entity, 'asset_tags'):
                tags_obj = getattr(entity, 'asset_tags')
                if tags_obj:
                    if isinstance(tags_obj, list):
                        for tag in tags_obj:
                            if hasattr(tag, 'name'):
                                asset_tags.append(tag.name)
                            elif hasattr(tag, 'value'):
                                asset_tags.append(tag.value)
                            elif hasattr(tag, 'display_name'):
                                asset_tags.append(tag.display_name)
                            elif isinstance(tag, str):
                                asset_tags.append(tag)
                            else:
                                asset_tags.append(str(tag))
                    else:
                        # Single tag object
                        if hasattr(tags_obj, 'name'):
                            asset_tags.append(tags_obj.name)
                        elif hasattr(tags_obj, 'value'):
                            asset_tags.append(tags_obj.value)
                        elif isinstance(tags_obj, str):
                            asset_tags.append(tags_obj)
                        else:
                            asset_tags.append(str(tags_obj))
            entity_dict["assetTags"] = asset_tags
            
            # Term type
            term_type = None
            if hasattr(entity, 'term_type'):
                type_obj = getattr(entity, 'term_type')
                if type_obj:
                    if hasattr(type_obj, 'value'):
                        term_type = type_obj.value
                    elif hasattr(type_obj, 'name'):
                        term_type = type_obj.name
                    elif isinstance(type_obj, str):
                        term_type = type_obj
                    else:
                        term_type = str(type_obj)
            entity_dict["termType"] = term_type
            
            # Display name
            display_name = None
            if hasattr(entity, 'display_name'):
                display_obj = getattr(entity, 'display_name')
                if display_obj:
                    if hasattr(display_obj, 'value'):
                        display_name = display_obj.value
                    elif hasattr(display_obj, 'text'):
                        display_name = display_obj.text
                    elif isinstance(display_obj, str):
                        display_name = display_obj
                    else:
                        display_name = str(display_obj)
            entity_dict["displayName"] = display_name
            
            # Abbreviation
            abbreviation = None
            if hasattr(entity, 'abbreviation'):
                abbrev_obj = getattr(entity, 'abbreviation')
                if abbrev_obj:
                    if hasattr(abbrev_obj, 'value'):
                        abbreviation = abbrev_obj.value
                    elif hasattr(abbrev_obj, 'text'):
                        abbreviation = abbrev_obj.text
                    elif isinstance(abbrev_obj, str):
                        abbreviation = abbrev_obj
                    else:
                        abbreviation = str(abbrev_obj)
            entity_dict["abbreviation"] = abbreviation
            
            # Examples
            examples = None
            if hasattr(entity, 'examples'):
                examples_obj = getattr(entity, 'examples')
                if examples_obj:
                    if hasattr(examples_obj, 'value'):
                        examples = examples_obj.value
                    elif hasattr(examples_obj, 'text'):
                        examples = examples_obj.text
                    elif isinstance(examples_obj, str):
                        examples = examples_obj
                    else:
                        examples = str(examples_obj)
            entity_dict["examples"] = examples
            
            # Readme
            readme = None
            if hasattr(entity, 'readme'):
                readme_obj = getattr(entity, 'readme')
                if readme_obj:
                    if hasattr(readme_obj, 'value'):
                        readme = readme_obj.value
                    elif hasattr(readme_obj, 'text'):
                        readme = readme_obj.text
                    elif isinstance(readme_obj, str):
                        readme = readme_obj
                    else:
                        readme = str(readme_obj)
            entity_dict["readme"] = readme
            
            # Connection name
            connection_name = None
            if hasattr(entity, 'connection_name'):
                conn_obj = getattr(entity, 'connection_name')
                if conn_obj:
                    if hasattr(conn_obj, 'value'):
                        connection_name = conn_obj.value
                    elif hasattr(conn_obj, 'name'):
                        connection_name = conn_obj.name
                    elif isinstance(conn_obj, str):
                        connection_name = conn_obj
                    else:
                        connection_name = str(conn_obj)
            entity_dict["connectionName"] = connection_name
            
            # Connector name
            connector_name = None
            if hasattr(entity, 'connector_name'):
                connector_obj = getattr(entity, 'connector_name')
                if connector_obj:
                    if hasattr(connector_obj, 'value'):
                        connector_name = connector_obj.value
                    elif hasattr(connector_obj, 'name'):
                        connector_name = connector_obj.name
                    elif isinstance(connector_obj, str):
                        connector_name = connector_obj
                    else:
                        connector_name = str(connector_obj)
            entity_dict["connectorName"] = connector_name
            
            # Meanings/related terms
            meaning_names = []
            if hasattr(entity, 'meanings'):
                meanings_obj = getattr(entity, 'meanings')
                if meanings_obj:
                    if isinstance(meanings_obj, list):
                        for meaning in meanings_obj:
                            if hasattr(meaning, 'displayText'):
                                meaning_names.append(meaning.displayText)
                            elif hasattr(meaning, 'name'):
                                meaning_names.append(meaning.name)
                            elif hasattr(meaning, 'value'):
                                meaning_names.append(meaning.value)
                            elif isinstance(meaning, str):
                                meaning_names.append(meaning)
                            else:
                                meaning_names.append(str(meaning))
                    else:
                        # Single meaning object
                        if hasattr(meanings_obj, 'displayText'):
                            meaning_names.append(meanings_obj.displayText)
                        elif hasattr(meanings_obj, 'name'):
                            meaning_names.append(meanings_obj.name)
                        elif hasattr(meanings_obj, 'value'):
                            meaning_names.append(meanings_obj.value)
                        elif isinstance(meanings_obj, str):
                            meaning_names.append(meanings_obj)
                        else:
                            meaning_names.append(str(meanings_obj))
            entity_dict["meaningNames"] = meaning_names
            
            print(f"DEBUG: Final processed entity: {entity_dict}")
            processed.append(entity_dict)
        return processed
    
    def get_term_by_guid(self, term_guid: str) -> Optional[Dict[str, Any]]:
        """Get a glossary term by its GUID"""
        try:
            term = self.client.get_asset_by_guid(term_guid, asset_type=AtlasGlossaryTerm)
            if term:
                return {
                    "guid": term.guid,
                    "name": term.name,
                    "qualifiedName": term.qualified_name,
                    "description": term.description,
                    "userDescription": term.user_description
                }
        except Exception as e:
            print(f"❌ Error getting term by GUID: {e}")
        
        return None
    
    def search_terms_by_name(self, term_name: str) -> List[Dict[str, Any]]:
        """Search for glossary terms by name using direct API call"""
        try:
            print(f"DEBUG: Searching for glossary term: {term_name}")
            
            # Construct search body specifically for glossary terms
            search_body = {
                "dsl": {
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"__typeName.keyword": "AtlasGlossaryTerm"}},
                                {"term": {"__state": "ACTIVE"}}
                            ],
                            "should": [
                                {"wildcard": {"name": f"*{term_name}*"}},
                                {"wildcard": {"displayName": f"*{term_name}*"}},
                                {"match": {"name": term_name}},
                                {"match": {"displayName": term_name}}
                            ],
                            "minimum_should_match": 1
                        }
                    }
                },
                "attributes": [
                    "name", "displayName", "description", "userDescription", "longDescription",
                    "qualifiedName", "guid", "certificateStatus", "ownerUsers", "ownerGroups",
                    "assetTags", "termType", "popularityScore", "starredCount", "abbreviation",
                    "examples", "readme", "connectorName", "connectionName", "meaningNames"
                ],
                "size": 10
            }
            
            print(f"DEBUG: Search body: {search_body}")
            
            # Make the API request
            url = f"{self.base_url}/api/meta/search/indexsearch"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            print(f"DEBUG: Making API request to: {url}")
            response = requests.post(url, json=search_body, headers=headers)
            print(f"DEBUG: Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: Response keys: {list(data.keys())}")
                
                # Extract entities from the response
                entities = []
                if 'entities' in data:
                    entities = data['entities']
                    print(f"DEBUG: Found entities in 'entities' key: {len(entities)}")
                elif 'hits' in data and 'hits' in data['hits']:
                    entities = [hit['_source'] for hit in data['hits']['hits']]
                    print(f"DEBUG: Found entities in 'hits' key: {len(entities)}")
                else:
                    print(f"DEBUG: No entities found in any expected key")
                    print(f"DEBUG: Available keys: {list(data.keys())}")
                
                print(f"DEBUG: Found {len(entities)} entities in search response")
                
                if entities:
                    # Process the entities using the same approach as the working version
                    results = []
                    for entity in entities:
                        if entity:
                            print(f"DEBUG: Processing entity: {entity.get('attributes', {}).get('name', 'Unknown')}")
                            # Extract attributes like the working version
                            result = self._extract_asset_attributes(entity)
                            if result:
                                results.append(result)
                                print(f"DEBUG: Successfully extracted attributes for: {result.get('name', 'Unknown')}")
                            else:
                                print(f"DEBUG: Failed to extract attributes for entity")
                    
                    print(f"DEBUG: Processed {len(results)} entities")
                    return results
                else:
                    print(f"DEBUG: No entities found")
                    return []
            else:
                print(f"DEBUG: Search request failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"DEBUG: Error in search_terms_by_name: {e}")
            return []
    
    def _extract_asset_attributes(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and flatten attributes from Atlan entity response."""
        try:
            # Debug: Print the full entity structure to understand what we're working with
            print(f"DEBUG: Full entity structure for {entity.get('name', 'Unknown')}:")
            print(f"DEBUG: Entity keys: {list(entity.keys())}")
            
            # The entity might be the full object or might have an 'attributes' key
            # Let's check both possibilities
            if 'attributes' in entity:
                attributes = entity['attributes']
                print(f"DEBUG: Found 'attributes' key with {len(attributes)} items")
            else:
                # If no 'attributes' key, use the entity itself
                attributes = entity
                print(f"DEBUG: Using entity directly as attributes")
            
            # Debug: Print available attributes to see what we're getting
            print(f"DEBUG: Available attributes: {list(attributes.keys())}")
            
            # Extract common fields with proper fallbacks - using camelCase keys to match UI expectations
            result = {
                'guid': entity.get('guid') or attributes.get('guid'),
                'typeName': entity.get('typeName') or attributes.get('typeName'),
                'name': (
                    attributes.get('name') or 
                    attributes.get('displayName') or 
                    entity.get('displayText') or 
                    entity.get('name') or
                    'Unknown'
                ),
                'displayName': (
                    attributes.get('displayName') or 
                    entity.get('displayText') or
                    attributes.get('name')
                ),
                # Priority: userDescription > description > longDescription > shortDescription  
                'description': (
                    attributes.get('userDescription') or 
                    attributes.get('description') or 
                    attributes.get('longDescription') or
                    attributes.get('shortDescription') or
                    entity.get('userDescription') or
                    entity.get('description') or
                    entity.get('longDescription') or
                    entity.get('shortDescription')
                ),
                'userDescription': (
                    attributes.get('userDescription') or
                    entity.get('userDescription')
                ),
                'longDescription': (
                    attributes.get('longDescription') or
                    entity.get('longDescription')
                ),
                'qualifiedName': (
                    attributes.get('qualifiedName') or
                    entity.get('qualifiedName')
                ),
                # Certificate status mapping
                'certificateStatus': (
                    attributes.get('certificateStatus') or 
                    attributes.get('certificationStatus') or
                    entity.get('certificateStatus') or
                    entity.get('certificationStatus') or
                    entity.get('status')
                ),
                'ownerUsers': (
                    attributes.get('ownerUsers') or 
                    entity.get('ownerUsers') or
                    []
                ),
                'ownerGroups': (
                    attributes.get('ownerGroups') or 
                    entity.get('ownerGroups') or
                    []
                ),
                'connectorName': (
                    attributes.get('connectorName') or
                    entity.get('connectorName')
                ),
                'connectionName': (
                    attributes.get('connectionName') or
                    entity.get('connectionName')
                ),
                'databaseName': (
                    attributes.get('databaseName') or
                    entity.get('databaseName')
                ),
                'schemaName': (
                    attributes.get('schemaName') or
                    entity.get('schemaName')
                ),
                'meanings': (
                    attributes.get('meanings') or 
                    entity.get('meanings') or
                    []
                ),
                'assetTags': (
                    attributes.get('assetTags') or 
                    entity.get('assetTags') or
                    []
                ),
                'categories': (
                    attributes.get('categories') or 
                    entity.get('categories') or
                    []
                ),
                'readme': (
                    attributes.get('readme') or 
                    entity.get('readme') or
                    {}
                ),
                'announcementTitle': (
                    attributes.get('announcementTitle') or
                    entity.get('announcementTitle')
                ),
                'announcementMessage': (
                    attributes.get('announcementMessage') or
                    entity.get('announcementMessage')
                ),
                'examples': (
                    attributes.get('examples') or 
                    entity.get('examples') or
                    []
                ),
                'abbreviation': (
                    attributes.get('abbreviation') or
                    entity.get('abbreviation')
                ),
                'termType': (
                    attributes.get('termType') or
                    entity.get('termType')
                ),
                'popularityScore': (
                    attributes.get('popularityScore') or
                    entity.get('popularityScore')
                ),
                'starredCount': (
                    attributes.get('starredCount') or
                    entity.get('starredCount')
                ),
                # Custom Score metadata badge
                'viewScore': (
                    attributes.get('viewScore') or
                    entity.get('viewScore')
                ),
                # Additional fields that might contain description-like content
                'information': (
                    attributes.get('information') or
                    entity.get('information')
                ),
                'summary': (
                    attributes.get('summary') or
                    entity.get('summary')
                ),
                'notes': (
                    attributes.get('notes') or
                    entity.get('notes')
                )
            }
            
            # If still no description, try to get it from readme
            if not result['description'] and result.get('readme'):
                if isinstance(result['readme'], dict):
                    readme_attrs = result['readme'].get('attributes', {})
                    result['description'] = readme_attrs.get('description') or readme_attrs.get('content')
                elif isinstance(result['readme'], str):
                    result['description'] = result['readme']
            
            # Clean up None values but keep empty strings and lists
            cleaned_result = {}
            for key, value in result.items():
                if value is not None:
                    cleaned_result[key] = value
            
            print(f"DEBUG: Final extracted result for {result.get('name', 'Unknown')}:")
            print(f"DEBUG: Description: {result.get('description', 'None')}")
            print(f"DEBUG: User Description: {result.get('userDescription', 'None')}")
            print(f"DEBUG: Certificate Status: {result.get('certificateStatus', 'None')}")
            print(f"DEBUG: Owner Users: {result.get('ownerUsers', 'None')}")
            
            return cleaned_result
            
        except Exception as e:
            print(f"Error extracting asset attributes: {e}")
            import traceback
            traceback.print_exc()
            return {} 