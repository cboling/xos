tosca_definitions_version: tosca_simple_yaml_1_0

# compile this with "m4 vaosservice.m4 > vaosservice.yaml"

# include macros
include(macros.m4)

node_types:
    tosca.nodes.VaosService:
        derived_from: tosca.nodes.Root
        description: >
            vAOS Service
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_props
            xos_base_service_props
            service_message:
                type: string
                required: false

    tosca.nodes.VaosTenant:
        derived_from: tosca.nodes.Root
        description: >
            A Tenant of the vAOS service
        properties:
            xos_base_tenant_props
            s_tag:
                type: string
                required: false
                description: s_tag, identifies which olt port
            c_tag:
                type: string
                required: false
                description: c_tag, identifies which subscriber within s_tag
