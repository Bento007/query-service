from dcpquery import config
from dcpquery.db.models.protocol import Protocol, ProtocolReagentJoinTable, SequencingProtocol, \
    LibraryPreparationProtocol, EnrichmentProtocol, AnalysisProtocol, IPSCInductionProtocol, DifferentiationProtocol
from dcpquery.etl.load.modules import get_or_create_ontology, get_or_create_reagent, get_or_create_ten_x, \
    get_or_create_barcode


def create_protocol(data):
    reagents_list = []
    method = get_or_create_ontology(data.get('method'))
    for reagent in data['reagents']:
        reagents_list.append(get_or_create_reagent(reagent))
    config.db_session.add_all(reagents_list)
    protocol = Protocol(
        method=method,
        protocol_id=data.get("protocol_core", {}).get("protocol_id"),
        body=data,
        name=data.get('protocol_name'),
        description=data.get('protocol_description'),
        publication_doi=data.get('publication_doi'),
    )
    for reagent in reagents_list:
        config.db_session.add(ProtocolReagentJoinTable(protocol=protocol, reagent=reagent))
    config.db_session.add(protocol)
    return protocol


def create_differentiation_protocol(data):
    reagents_list = []
    method = get_or_create_ontology(data.get('method'))
    for reagent in data['reagents']:
        reagents_list.append(get_or_create_reagent(reagent))
    config.db_session.add_all(reagents_list)
    differentiation_protocol = DifferentiationProtocol(
        method=method,
        protocol_id=data.get("protocol_core", {}).get("protocol_id"),
        body=data,
        name=data.get('protocol_name'),
        description=data.get('protocol_description'),
        publication_doi=data.get('publication_doi'),
        media=data.get('media'),
        small_molecules=data.get('small_molecules'),
        target_cell_yield=int(data.get('target_cell_yield')),
        target_pathway=data.get('target_pathway'),
        validation_method=data.get('validation_method'),
        validation_result=data.get('validation_result')
    )
    for reagent in reagents_list:
        config.db_session.add(ProtocolReagentJoinTable(protocol=differentiation_protocol, reagent=reagent))
    config.db_session.add(differentiation_protocol)
    return differentiation_protocol


def create_library_preparation_protocol(data):
    reagents_list = []
    method = get_or_create_ontology(data.get('library_construction_method'))
    cell_barcode = get_or_create_barcode(data.get('cell_barcode'))
    umi_barcode = get_or_create_ontology(data.get('umi_barcode'))
    library_preamplification_method = get_or_create_ontology((data.get('library_preamplification_method')))
    cdna_library_amplification_method = get_or_create_ontology(data.get('cdna_library_amplification_method'))
    library_construction_kit = get_or_create_reagent(data.get('library_construction_kit'))
    nucleic_acid_conversion_kit = get_or_create_reagent(data.get('nucleic_acid_conversion_kit'))
    spike_in_kit = get_or_create_reagent(data.get('nucleic_acid_conversion_kit'))
    for reagent in data['reagents']:
        reagents_list.append(get_or_create_reagent(reagent))
    config.db_session.add_all(reagents_list)
    library_protocol = LibraryPreparationProtocol(
        method=method,
        protocol_id=data.get("protocol_core", {}).get("protocol_id"),
        body=data,
        name=data.get('protocol_name'),
        description=data.get('protocol_description'),
        publication_doi=data.get('publication_doi'),
        nucleic_acid_source=data.get('nucleic_acid_source'),
        end_bias=data.get('end_bias'),
        strand=data.get('strand'),
        cell_barcode=cell_barcode,
        umi_barcode=umi_barcode,
        primer=data.get('primer'),
        nominal_length=int(data.get('nominal_length')),
        # todo look up
        nominal_sdev=int(data.get('nominal_sdev')),
        spike_in_dilution=int(data.get('spike_in_dilution')),
        library_preamplification_method=library_preamplification_method,
        cdna_library_amplification_method=cdna_library_amplification_method,
        library_construction_kit=library_construction_kit,
        nucleic_acid_conversion_kit=nucleic_acid_conversion_kit,
        spike_in_kit=spike_in_kit
    )
    for reagent in reagents_list:
        config.db_session.add(ProtocolReagentJoinTable(protocol=library_protocol, reagent=reagent))
    config.db_session.add(library_protocol)
    return library_protocol


def create_sequencing_protocol(data):
    reagents_list = []
    method = get_or_create_ontology(data.get('method'))
    for reagent in data.get('reagents'):
        reagents_list.append(get_or_create_reagent(reagent))

    # Todo check syntax
    tenx = get_or_create_ten_x(data.get('10x'))
    sequencing_protocol = SequencingProtocol(
        method=method,
        discriminator='sequencing_protocol',
        protocol_id=data.get("protocol_core", {}).get("protocol_id"),
        body=data,
        name=data.get('name'),
        description=data.get('description'),
        publication_doi=data.get('publication_doi'),
        instrument_manufacturer_model=get_or_create_ontology(data.get('instrument_manufacturer_model')),
        paired_end=data.get('paired_end'),
        ten_x=tenx,
        local_machine_name=data.get('local_machine_name')
    )
    config.db_session.add(sequencing_protocol)
    for reagent in reagents_list:
        config.db_session.add(ProtocolReagentJoinTable(protocol=sequencing_protocol, reagent=reagent))
    config.db_session.add_all(reagents_list)


def create_enrichment_protocol(data):
    reagents_list = []
    method = get_or_create_ontology(data.get('method'))
    for reagent in data['reagents']:
        reagents_list.append(get_or_create_reagent(reagent))
    config.db_session.add_all(reagents_list)
    enrichment_protocol = EnrichmentProtocol(
        method=method,
        discriminator='enrichment_protocol',
        protocol_id=data.get("protocol_core", {}).get("protocol_id"),
        body=data,
        name=data.get('protocol_name'),
        description=data.get('protocol_description'),
        publication_doi=data.get('publication_doi'),
        markers=data.get('markers'),
        minimum_size=int(data.get('minimum')),
        maximum_size=int(data.get('maximum'))
    )
    for reagent in reagents_list:
        config.db_session.add(ProtocolReagentJoinTable(protocol=enrichment_protocol, reagent=reagent))
    config.db_session.add(enrichment_protocol)
    return enrichment_protocol


def create_collection_protocol(data):
    protocol = create_protocol(data)
    protocol.discriminator = 'collection_protocol'
    return protocol


def create_dissociation_protocol(data):
    protocol = create_protocol(data)
    protocol.discriminator = 'dissociation_protocol'
    return protocol


def create_analysis_protocol(data):
    reagents_list = []
    method = get_or_create_ontology(data.get('method'))
    type = get_or_create_ontology(data.get('type'))
    for reagent in data['reagents']:
        reagents_list.append(get_or_create_reagent(reagent))
    config.db_session.add_all(reagents_list)
    analysis_protocol = AnalysisProtocol(
        method=method,
        protocol_id=data.get("protocol_core", {}).get("protocol_id"),
        body=data,
        name=data.get('protocol_name'),
        description=data.get('protocol_description'),
        publication_doi=data.get('publication_doi'),
        computational_method=data.get('computational_method'),
        type=type
    )
    for reagent in reagents_list:
        config.db_session.add(ProtocolReagentJoinTable(protocol=analysis_protocol, reagent=reagent))
    config.db_session.add(analysis_protocol)
    return analysis_protocol


def create_ipsc_induction_protocol(data):
    reagents_list = []
    method = get_or_create_ontology(data.get('method'))
    ipsc_induction_kit = get_or_create_reagent(data.get('ipsc_induction_kit'))
    for reagent in data['reagents']:
        reagents_list.append(get_or_create_reagent(reagent))
    config.db_session.add_all(reagents_list)
    ipsc_protocol = IPSCInductionProtocol(
        method=method,
        protocol_id=data.get("protocol_core", {}).get("protocol_id"),
        body=data,
        name=data.get('protocol_name'),
        description=data.get('protocol_description'),
        publication_doi=data.get('publication_doi'),
        reprogramming_factors=data.get('reprogramming_factors'),
        ipsc_induction_kit=ipsc_induction_kit,
        pluripotency_test=data.get('pluripotency_test'),
        percent_pluripotency=int(data.get('percent_pluripotency')),
        pluripotency_vector_removed=data.get('pluripotency_vector_removed')

    )
    for reagent in reagents_list:
        config.db_session.add(ProtocolReagentJoinTable(protocol=ipsc_protocol, reagent=reagent))
    config.db_session.add(ipsc_protocol)
    return ipsc_protocol
