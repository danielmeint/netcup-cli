"""
DNS-specific operations for netcup API.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .client import NetcupAPIClient, APIResponse


class DNSRecord(BaseModel):
    """Model for a DNS record."""
    
    id: Optional[str] = None
    hostname: str
    type: str
    priority: Optional[str] = None
    destination: str
    deleterecord: Optional[bool] = None
    state: Optional[str] = None


class DNSZone(BaseModel):
    """Model for a DNS zone."""
    
    name: str
    ttl: Optional[str] = None
    serial: Optional[str] = None
    refresh: Optional[str] = None
    retry: Optional[str] = None
    expire: Optional[str] = None
    dnssecstatus: Optional[bool] = None


class DNSManager:
    """Manages DNS operations via the netcup API."""
    
    def __init__(self, api_client: NetcupAPIClient):
        self.api_client = api_client
    
    def get_zone_info(self, domain: str) -> DNSZone:
        """
        Get information about a DNS zone.
        
        Args:
            domain: The domain name
            
        Returns:
            DNSZone: The zone information
        """
        params = {"domainname": domain}
        response = self.api_client.make_authenticated_request("infoDnsZone", params)
        
        if not response.responsedata or not isinstance(response.responsedata, dict):
            raise ValueError(f"No zone data returned for domain: {domain}")
        
        return DNSZone(**response.responsedata)
    
    def get_records(self, domain: str) -> List[DNSRecord]:
        """
        Get all DNS records for a domain.
        
        Args:
            domain: The domain name
            
        Returns:
            List[DNSRecord]: List of DNS records
        """
        params = {"domainname": domain}
        response = self.api_client.make_authenticated_request("infoDnsRecords", params)
        
        # Handle different responsedata types
        if not response.responsedata:
            return []
            
        if isinstance(response.responsedata, dict) and "dnsrecords" in response.responsedata:
            records_data = response.responsedata["dnsrecords"]
            if isinstance(records_data, list):
                return [DNSRecord(**record) for record in records_data]
        
        return []
    
    def update_records(self, domain: str, records: List[DNSRecord]) -> bool:
        """
        Update DNS records for a domain.
        
        Args:
            domain: The domain name
            records: List of DNS records to update
            
        Returns:
            bool: True if successful
        """
        # Convert records to the format expected by the API
        records_data = []
        for record in records:
            record_dict = record.model_dump(exclude_none=True)
            records_data.append(record_dict)
        
        params = {
            "domainname": domain,
            "dnsrecordset": {
                "dnsrecords": records_data
            }
        }
        
        response = self.api_client.make_authenticated_request("updateDnsRecords", params)
        return response.statuscode < 4000
    
    def add_record(
        self, 
        domain: str, 
        hostname: str, 
        record_type: str, 
        destination: str,
        priority: Optional[str] = None
    ) -> bool:
        """
        Add a new DNS record.
        
        Args:
            domain: The domain name
            hostname: The hostname for the record
            record_type: The DNS record type (A, AAAA, CNAME, etc.)
            destination: The destination/target for the record
            priority: Priority for MX records
            
        Returns:
            bool: True if successful
        """
        # Get existing records
        existing_records = self.get_records(domain)
        
        # Create new record
        new_record = DNSRecord(
            hostname=hostname,
            type=record_type,
            destination=destination,
            priority=priority
        )
        
        # Add to existing records
        all_records = existing_records + [new_record]
        
        return self.update_records(domain, all_records)
    
    def delete_record(self, domain: str, record_id: str) -> bool:
        """
        Delete a DNS record.
        
        Args:
            domain: The domain name
            record_id: The ID of the record to delete
            
        Returns:
            bool: True if successful
        """
        # Get existing records
        existing_records = self.get_records(domain)
        
        # Find and mark the record for deletion
        record_found = False
        for record in existing_records:
            if record.id == record_id:
                record.deleterecord = True
                record_found = True
                break
        
        if not record_found:
            raise ValueError(f"Record with ID {record_id} not found")
        
        return self.update_records(domain, existing_records)
    
    def update_record(
        self,
        domain: str,
        record_id: str,
        hostname: Optional[str] = None,
        destination: Optional[str] = None,
        priority: Optional[str] = None
    ) -> bool:
        """
        Update an existing DNS record.
        
        Args:
            domain: The domain name
            record_id: The ID of the record to update
            hostname: New hostname (optional)
            destination: New destination (optional)
            priority: New priority (optional)
            
        Returns:
            bool: True if successful
        """
        # Get existing records
        existing_records = self.get_records(domain)
        
        # Find and update the record
        record_found = False
        for record in existing_records:
            if record.id == record_id:
                if hostname is not None:
                    record.hostname = hostname
                if destination is not None:
                    record.destination = destination
                if priority is not None:
                    record.priority = priority
                record_found = True
                break
        
        if not record_found:
            raise ValueError(f"Record with ID {record_id} not found")
        
        return self.update_records(domain, existing_records)
    
    def list_domains(self) -> List[str]:
        """
        Get a list of domains (this would need domain reseller API).
        For now, this is a placeholder that could be extended.
        
        Returns:
            List[str]: List of domain names
        """
        # This functionality would require the domain reseller API
        # For now, we'll return an empty list and suggest users specify domains directly
        return [] 