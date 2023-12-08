from neo4j import GraphDatabase


class Neo4jConnection:

    def __init__(self, uri, userName, password):
        self.driver = GraphDatabase.driver(uri=uri, auth=(userName, password))

    def close(self):
        self.driver.close()

    def check_connection(self):
        try:
            self.driver.verify_connectivity()
        except:
            return False
        return True

    def check_authentification(self):
        result = self.driver.verify_authentication()
        return result

    def create_journey_tx(self, tx, journey):
        q_create_journey = f''' Merge (l:Journey:Entity {{{journey}, EntityType: "Journey"}})'''
        print(q_create_journey)
        tx.run(q_create_journey)

    def create_journey(self, journey_query, session):
        session.execute_write(self.create_journey_tx, journey_query)

    def create_log(self, file_name, time_stamp, session):
        session.execute_write(self.create_log_tx, file_name, time_stamp)

    def create_log_tx(self, tx, file_name, time_stamp):
        q_create_log = f'''MERGE  (en:Log {{fileName:"{file_name}",
        timeStamp:{time_stamp}}})'''
        print(q_create_log)
        tx.run(q_create_log)

    def associate_log_with_journey(self, session, log_where,
                                   file_name, time_stamp):
        session.execute_write(self.associate_log_with_journey_tx, log_where,
                              file_name, time_stamp)

    def associate_log_with_journey_tx(self, tx,  log_where,
                                      file_name, time_stamp):
        q_associate_log_with_journey = f'''
        MATCH (l:Log {{fileName:"{file_name}",timeStamp:{time_stamp}}})
        MATCH (j:Journey {{{log_where}}})
        MERGE (l)-[:Has]->(j)
        '''
        print(q_associate_log_with_journey)
        tx.run(q_associate_log_with_journey)

    def create_event_tx(self, tx, attributes):
        column = "{"
        q_Create_Event = ' Create (e:Event  '
        column += attributes
        q_Create_Event += column
        q_Create_Event += ", Activity:TouchpointEvent"
        q_Create_Event += "})"
        print(q_Create_Event)
        tx.run(q_Create_Event)

    def create_subevent(self, attributes, session):
        session.execute_write(self.create_subevent_tx, attributes)

    def create_subevent_tx(self, tx, attributes):
        q_create_subevent = f'''Create (n: Event {{{attributes}}})'''
        print(q_create_subevent)
        tx.run(q_create_subevent)

    def create_event(self, event, session):
        session.execute_write(self.create_event_tx, event)

    def create_entity(self, insert_values, node_exists, session, identifier=""):
        if node_exists:
            session.execute_write(self.update_Entity_tx,
                                  insert_values,
                                  identifier)
        else:
            session.execute_write(self.create_Entity_tx, insert_values)

    def create_Entity_tx(self, tx, insert_values):
        q_create_entity = f'''
        MERGE (en:Entity {{{insert_values}}})'''
        print(q_create_entity)
        tx.run(q_create_entity)

    def add_journey(self, connection, journeyID):
        qAddJourney = f''' Create (:Journey:Entity {{ID: "{journeyID}", EntityType="{"Journey"}"}})'''
        print(qAddJourney)
        connection.run(qAddJourney)

    def create_connection_event_journey(self, event_where, journey_where,
                                        match, session):
        session.execute_write(self.connect_journey_to_event, journey_where,
                              event_where, match)

    def connect_journey_to_event(self, connection, journey_where, 
                                 event_where, match):
        q_link_events_to_journey = f'''
            MATCH (en:Touchpoint {{{event_where}}})
            MATCH (e: Journey {{{journey_where}}})
            WHERE {match}
            MERGE (e)-[:Contains]->(en)
        '''
        print(q_link_events_to_journey)
        connection.run(q_link_events_to_journey)

    def create_entity_event_relationship(self, connection,
                                         where_clause,
                                         query_to_get_event_node,
                                         match_clause,
                                         type_of_connection,
                                         properties):
        q_entity_event_relationship = f'''
        MATCH (e: Touchpoint WHERE {where_clause}),
        (ev:Event WHERE {query_to_get_event_node})
        MATCH (en:Entity WHERE {match_clause})
        MERGE (e)-[{type_of_connection}:{type_of_connection}
        {{{properties}}}]->(en)'''

        print(q_entity_event_relationship)
        connection.run(q_entity_event_relationship)

    def create_connection_event_entity(self, where_clause,
                                       query_to_get_event_node, field_name,
                                       type_of_connection, properties,
                                       session):
        session.execute_write(self.create_entity_event_relationship,
                              where_clause, query_to_get_event_node,
                              field_name, type_of_connection, properties)

    def create_direct_event_flow(self, connection, jounreyID):
        q_direct_event_flow = f'''MATCH (n: Entity)
        MATCH (n)<-[:Corr]- ( ev WHERE ev.journey = {jounreyID})
        WITH n, ev as events ORDER BY ev.timestamp, elementId(e)
        WITH n, collect( events ) AS eventList
        UNWIND range(0,size(eventList) -2 ) AS i
        WITH n, eventList[i] as e1, eventList[i+1] as e2
        MERGE (e1)-[df:Df [EntityType:n.EntityType]]->(e2)
        '''
        connection.run(q_direct_event_flow)

    def create_relation_between_entities(connection,
                                         EndUserType, OtherType,
                                         relationType):
        q_create_relation_between_entities = f'''
        MATCH (e1:Event)-[:Corr]->(n1:Entity)
        WHERE n1.EntityType='{EndUserType}'
        MATCH (e2:Event)-[:Corr]->(n2:Entity) W
        HERE n2.EntityType='{OtherType}'
        AND e1 <> e2 AND e2.userID = n1.ID
        WITH DISTINCT n1.ID as n1_id, n2.ID as n2_id
        WHERE n1_id <> 'UNKNOWN' AND n2_id <> 'UNKNOWN'
        CREATE (n1) <-[:REL {{Type:{relationType}}}] - (n2)
        '''
        print(q_create_relation_between_entities)
        connection.run(q_create_relation_between_entities)

    def reify_relations_between_entities(connection, typeR):
        q_reify_relations_between_entities = f'''
        MATCH (n1:Entity)-[rel:REL {{Type:'{typeR}'}}]->(n2:Entity)
        CREATE (n1)<-[:REL {{Type:'Reified'}}]-(r :Entity {{ID:n1.ID+'_'+n2.ID,
        EntityType:'{typeR}',
        uID:'{typeR}_'+n1.id+'_'+n2.id}})-[:REL {{Type:'Reified'}}]->(n2)
        '''

        connection.run(q_reify_relations_between_entities)

        q_correaleted_relationship = f'''
        MATCH (e:Event) -[:Corr]->(n:Entity)<-[:REL {{Type:'Reified'}}]-
        (r:Entity {{EntityType:'{typeR}'}})
        CREATE (e)-[:Corr]->(r)
        '''

        connection.run(q_correaleted_relationship)

    def create_directly_follows_tx(self, journey, session):
        session.execute_write(self.create_directly_follows, journey)

    def create_directly_follows(self, tx, journey):
        qCreateDf = f'''
        MATCH (b:Event)
        WHERE b.journey = "{journey}"
        WITH b
        ORDER BY b.timestamp
        WITH collect(b) AS nodes
        UNWIND range(0,size(nodes) -2 ) AS i
        WITH nodes[i] as e1, nodes[i+1] as e2
        MERGE (e1)-[:Df]->(e2)'''
        print(qCreateDf)
        tx.run(qCreateDf)

    def create_class(self, insert, session, is_planned=False):
        session.execute_write(self.create_class_tx, insert, is_planned)

    def create_class_tx(self, tx, insert, is_planned):
        full_properties = insert + ", Type" + ":\"Touchpoint\""
        q_create_class = f'''
        CREATE (c:Touchpoint{ ":Class" if is_planned else "" } {{{full_properties}}} )
        '''
        print(q_create_class)
        tx.run(q_create_class)

    def create_class_event_relationship(self, id, jounreyID, session):
        session.execute_write(self.create_class_event_relationship_tx,
                              id, jounreyID)

    def create_class_event_relationship_tx(self, tx, id, jounreyID):
        q_create_relationship = f'''
        MATCH (e:Event WHERE e.Id = "{id}" and e.journey = "{jounreyID}"),
        (c:Touchpoint WHERE c.Id = "{id}" and c.journey = "{jounreyID}")
        MERGE (e)-[:Observe]->(c)
        '''
        print(q_create_relationship)
        tx.run(q_create_relationship)

    def check_node_existance(self, query, session):
        result = session.execute_read(self.check_node_existance_tx, query)
        return result

    def check_node_existance_tx(self, tx, query):
        q_check_node_existance = f'''MATCH (e:Entity {{{query}}})
        return e'''
        record = tx.run(q_check_node_existance)
        if (record.single() is None):
            return False
        return True

    def update_Entity_tx(self, tx, query, identifier):
        q_update_entity = f'''MATCH (e:Entity {{{identifier}}})
        SET {query}'''
        print(q_update_entity)
        tx.run(q_update_entity)

    def create_communication_node(self, session, channel):
        session.execute_write(self.create_communication_node_tx, channel)

    def create_communication_node_tx(self, tx, channel):
        q_merge_channel = f'''MERGE (c:Channel {{Channel:"{channel}"}})'''
        tx.run(q_merge_channel)

    def associate_class_and_communication(self, channel_name,
                                          actor_where, session):
        session.execute_write(self.associate_class_and_communication_tx,
                              channel_name, actor_where)

    def associate_class_and_communication_tx(self, tx,
                                             channel_name, actor_where):
        q_associate_channel_touchpoint = f'''MATCH (c:Channel
        {{Channel:"{channel_name}"}})
        MATCH (e:Entity {{{actor_where}}})
        MERGE (e)-[:Communicated]->(c)
        '''
        print(q_associate_channel_touchpoint)
        tx.run(q_associate_channel_touchpoint)

    def associate_experience_with_journey(self, session, journey_data,
                                          properties):
        session.execute_write(self.associate_experience_with_journey_tx,
                              journey_data, properties)

    def associate_experience_with_Journey(self, where_clause,
                                             properties, session):
        session.execute_write(self.associate_experience_with_journey_tx,
                              where_clause, properties)

    def associate_experience_with_touchpoint(self, session, where_clause,
                                             jounreyID,
                                             properties):
        session.execute_write(self.associate_experience_with_touchpoint_tx,
                              where_clause, jounreyID, properties)

    def associate_experience_with_journey_tx(self, tx,
                                             journey_data, properties):
        q_create_node_and_relationship = f'''MATCH (j:Journey {{journey: "{journey_data}"}})
        MERGE (j) -[r:rates] ->(e:Experience {{{properties}}})'''
        tx.run(q_create_node_and_relationship)

    def associate_experience_with_touchpoint_tx(self, tx,
                                                where_clause, jounreyID, properties):
        q_create_node_and_relationship = f'''MATCH (j:Touchpoint {{{where_clause }, {jounreyID}}})
        Create (j) -[r:rates] ->(e:Experience {{{properties}}})'''
        tx.run(q_create_node_and_relationship)

    def associate_object_with_touchpoint(self, session,
                                         where_clause, properties):
        session.execute_write(self.associate_object_with_touchpoint_tx,
                              where_clause, properties)

    def associate_object_with_touchpoint_tx(self, tx,
                                            where_clause, properties):
        q_create_object_with_touchpoint = f'''MATCH (j:Touchpoint {{{where_clause}}})
        Create (j) -[r:belongs] ->(e:Object {{{properties}}})'''
        tx.run(q_create_object_with_touchpoint)

    def create_planned_touchpoint_connection(self, session, journey):
        session.execute_write(self.tx_create_planned_touchpoint_connection, journey)

    def tx_create_planned_touchpoint_connection(self, connection, journey):
        q_direct_event_flow = f'''MATCH (n: Class)
        WHERE n.journey = "{journey}"
        WITH n ORDER BY n.id
        WITH collect(n) AS nodeList
        UNWIND range(0, size(nodeList) - 2) AS i
        WITH nodeList[i] as e1, nodeList[i+1] as e2
        MERGE (e1)<-[:Depends]-(e2)
        '''
        connection.run(q_direct_event_flow)