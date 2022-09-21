import json

from datetime import datetime
from typing import Union

from sqlalchemy import true

from ..model import MapperFields, AuthTokenBaseModel

from mosip_token_seeder.tokenseeder.utils import NestedJsonUtils

class MappingService:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.nested_json_utils = NestedJsonUtils()
        self.mandatory_validation_auth_fields = config.authtoken.mandatory_validation_auth_fields.split(',')

    def validate_auth_data(self, authdata : dict, mapping: MapperFields, language):

        #"." is used to identify if the target auth_data is having any nested json.
        #for eg. if vid is inside a json object qrcodedata the mapping definition could be qrcodedata.vid

        final_dict = {}
        
        if not self.nested_json_utils.whether_nested_field_in(mapping.vid, authdata):
            return None, 'ATS-REQ-009'
        authdata_vid = self.nested_json_utils.extract_nested_value(mapping.vid, authdata)
        # if len(authdata_vid) <= 16 and len(authdata_vid) >= 19:
        #     return None, 'ATS-REQ-002'
        final_dict['vid'] = authdata_vid

        name_arr = []
        for name_var in mapping.name:
            authdata_name_var = self.nested_json_utils.extract_nested_value(name_var, authdata)
            if authdata_name_var:
                name_arr.append(authdata_name_var)
        authdata_name = self.config.root.name_delimiter.join(name_arr)
        if 'name' in self.mandatory_validation_auth_fields:
            if not authdata_name:
                return None, 'ATS-REQ-010'
            if len(authdata_name) == 0:
                return None, 'ATS-REQ-003'
        if authdata_name:
            final_dict['name'] = [{'language':language,'value': authdata_name}]

        authdata_gender = self.nested_json_utils.extract_nested_value(mapping.gender, authdata)
        if 'gender' in self.mandatory_validation_auth_fields:
            if not self.nested_json_utils.whether_nested_field_in(mapping.gender, authdata):
                return None, 'ATS-REQ-011'
            elif len(authdata_gender) == 0:
                return None, 'ATS-REQ-004'
            # if len(authdata_gender) > 256:
            #     return None, 'ATS-REQ-003'
            # if authdata_gender.lower() not in ['male','female','others']:
            #     return None, 'ATS-REQ-005'
        if authdata_gender:
            final_dict['gender'] = [{'language':language,'value': authdata_gender}]

        authdata_dob = self.nested_json_utils.extract_nested_value(mapping.dob, authdata)
        if 'dob' in self.mandatory_validation_auth_fields:
            if not self.nested_json_utils.whether_nested_field_in(mapping.dob, authdata):
                return None, 'ATS-REQ-012'
            if len(authdata_dob) == 0:
                return False, 'ATS-REQ-006'
        if authdata_dob:
            # try:
            #     if bool(datetime.strptime(authdata_dob, '%Y/%m/%d')) == False:
            #         return None, 'ATS-REQ-007'
            # except ValueError:
            #     return None, 'ATS-REQ-007'
            final_dict['dob'] = authdata_dob
            
        authdata_phone = self.nested_json_utils.extract_nested_value(mapping.phoneNumber, authdata)
        if 'phoneNumber' in self.mandatory_validation_auth_fields:
            if not self.nested_json_utils.whether_nested_field_in(mapping.phoneNumber, authdata):
                return None, 'ATS-REQ-013'
            # removed phone validation
        if authdata_phone:
            final_dict['phoneNumber'] = authdata_phone

        authdata_email = self.nested_json_utils.extract_nested_value(mapping.emailId, authdata)
        if 'emailId' in self.mandatory_validation_auth_fields:
            if not self.nested_json_utils.whether_nested_field_in(mapping.emailId, authdata):
                return None, 'ATS-REQ-014'
            # removed emailId validation
        if authdata_email:
            final_dict['emailId'] = authdata_email

        addr_arr = []
        for addr in mapping.fullAddress:
            addr_val  = self.nested_json_utils.extract_nested_value(addr, authdata)
            if addr_val:
                addr_arr.append(addr_val)
        authdata_addr = self.config.root.full_address_delimiter.join(addr_arr)
        if 'fullAddress' in self.mandatory_validation_auth_fields:
            if not authdata_addr:
                return None, 'ATS-REQ-015'
            if len(authdata_addr) == 0:
                return False, 'ATS-REQ-008'
        if authdata_addr:
            final_dict['fullAddress'] = [{'language':language,'value': authdata_addr}]

        return AuthTokenBaseModel(**final_dict),""
