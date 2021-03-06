#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

import warnings
from typing import List

from spacy.tokens.doc import Doc
from tqdm import tqdm

from match_text_unsafe.build_entity_dictionary import EntityTypename
from xml_extractions.extract_node_values import get_paragraph_from_file
from annotate_case.annotate_case import complete_case_annotations
from ner.model_factory import get_empty_model
from resources.config_provider import get_config_default
from viewer.spacy_viewer import view_spacy_docs

warnings.filterwarnings('ignore')

config_training = get_config_default()
model_dir_path = config_training["model_dir_path"]
xml_dev_path = config_training["xml_dev_path"]
number_of_paragraph_to_display = int(config_training["number_of_paragraph_to_display"])

nlp = get_empty_model(load_labels_for_training=False)
nlp = nlp.from_disk(model_dir_path)

DEV_DATA = get_paragraph_from_file(xml_dev_path,
                                   keep_paragraph_without_annotation=True)

all_docs_to_view: List[Doc] = list()
# last_case_spans = dict()
last_case_docs: List[Doc] = list()
former_case_id = None
entity_typename_builder = EntityTypename()

with tqdm(total=len(DEV_DATA[:number_of_paragraph_to_display]), unit=" paragraphs", desc="Find entities") as progress_bar:
    for (case_id, original_text, _, _) in DEV_DATA[:number_of_paragraph_to_display]:
        if case_id != former_case_id:
            spans = entity_typename_builder.get_dict()
            complete_case_annotations(last_case_docs, spans)

            all_docs_to_view.extend(last_case_docs)
            last_case_docs.clear()
            entity_typename_builder.clear()
            former_case_id = case_id
        spacy_doc: Doc = nlp(original_text)
        # doc.user_data['title'] = case_id
        last_case_docs.append(spacy_doc)
        # entities_span = [(ent.text.lower(), ent.label_) for ent in spacy_doc.ents]
        # last_case_spans.update(entities_span)
        entity_typename_builder.add_spacy_entities(spacy_doc=spacy_doc)
        progress_bar.update()

print("Generate HTML")
view_spacy_docs(all_docs_to_view, port=5000)
print("view result on browser (port 5000)")
