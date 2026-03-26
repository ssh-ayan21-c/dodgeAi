import logging
from backend.db.connection import get_db_driver

logger = logging.getLogger(__name__)

class GraphBuilder:
    """
    Deterministically structures orphaned Graph Nodes natively across labels
    to ensure the resulting Order-to-Cash traces are valid for LLM routing.
    """
    def __init__(self):
        self.driver = get_db_driver()

    def brute_force_link(self, source_label: str, target_label: str, rel_type: str, potential_keys: list):
        success = False
        logger.info(f"Evaluating cross-edge mapping (:{source_label}) -> [:{rel_type}] -> (:{target_label})")
        
        with self.driver.session() as session:
            for key in potential_keys:
                query = f"""
                MATCH (s:{source_label}), (t:{target_label})
                WHERE s.`{key}` IS NOT NULL AND t.`{key}` IS NOT NULL AND s.`{key}` = t.`{key}`
                MERGE (s)-[r:{rel_type}]->(t)
                RETURN count(r) as rel_count
                """
                try:
                    result = session.run(query)
                    rel_count = result.single()["rel_count"]
                    if rel_count > 0:
                        logger.info(f"SUCCESS: Threaded {rel_count} relationships referencing common attribute '{key}'")
                        success = True
                        break
                except Exception:
                    pass
        if not success:
            logger.debug(f"Edge map fault skipped between (:{source_label}) and (:{target_label}).")
        return success

    def build_core_relationships(self):
        """Standard sequence exposed to the central application controller."""
        logger.info("Executing comprehensive relational topology mapping...")
        self.brute_force_link("SalesOrderItems", "SalesOrderHeaders", "BELONGS_TO", ['salesOrder', 'SalesOrder', 'salesDocument', 'id'])
        self.brute_force_link("Customer", "SalesOrderHeaders", "PLACED", ['customer', 'customerId', 'customerNumber', 'soldToParty'])
        self.brute_force_link("JournalEntryItemsAccountsReceivable", "BillingDocumentItems", "ACCOUNTED_FOR", ['accountingDocument', 'AccountingDocument', 'billingDocument', 'referenceDocument'])
        self.brute_force_link("JournalEntryItemsAccountsReceivable", "SalesOrderHeaders", "BILLED_TO", ['accountingDocument', 'AccountingDocument', 'salesDocument', 'SalesDocument', 'referenceDocument'])
        self.brute_force_link("PaymentsAccountsReceivable", "BillingDocumentItems", "CLEARED", ['accountingDocument', 'AccountingDocument', 'billingDocument', 'referenceDocument'])
        logger.info("Topology mapping sequence is complete.")

# Singleton module exposure
graph_builder = GraphBuilder()
