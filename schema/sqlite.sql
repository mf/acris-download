CREATE TABLE IF NOT EXISTS country_codes (
    recordtype text,
    countrycode text,
    countrydescription text
);

CREATE TABLE IF NOT EXISTS document_control_codes (
    recordtype text,
    doctype text,
    doctypedescription text,
    classcodedescription text,
    party1type text,
    party2type text,
    party3type text
);

CREATE TABLE IF NOT EXISTS property_type_codes (
    recordtype text,
    propertytype text,
    typedescription text
);

CREATE TABLE IF NOT EXISTS real_property_legals (
    documentid text not null,
    recordtype text,
    borough integer,
    block integer,
    lot integer,
    easement text,
    partiallot text,
    airrights text,
    subterraneanrights text,
    propertytype text,
    streetnumber text,
    streetname text,
    unit text,
    goodthroughdate text
);

CREATE TABLE IF NOT EXISTS real_property_master (
    documentid text not null,
    recordtype text,
    crfn bigint,
    borough integer,
    doctype text,
    docdate text,
    docamount numeric,
    recordedfiled text,
    modifieddate text,
    reelyear integer,
    reelnbr integer,
    reelpage integer,
    perctransferred numeric,
    goodthroughdate text
);

CREATE TABLE IF NOT EXISTS real_property_parties (
    documentid text not null,
    recordtype text,
    partytype integer,
    name text,
    address1 text,
    address2 text,
    country text,
    city text,
    state text,
    zip text,
    goodthroughdate text
);

CREATE TABLE IF NOT EXISTS real_property_references (
    documentid text not null,
    recordtype text,
    referencebycrfn text,
    referencebydocid text,
    referencebyreelyear integer,
    referencebyreelborough integer,
    referencebyreelnbr integer,
    referencebyreelpage integer,
    not_used_1 text,
    not_used_2 text,
    goodthroughdate text
);

CREATE TABLE IF NOT EXISTS real_property_remarks (
    documentid text not null,
    recordtype text,
    sequencenumber integer,
    remarktext text,
    goodthroughdate text
);

CREATE TABLE IF NOT EXISTS ucc_collateral_codes (
    recordtype text,
    ucccollateralcode text,
    codedescription text
);
