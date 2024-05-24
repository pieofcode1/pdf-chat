import os
import sys
import dotenv
from pathlib import Path
import base64
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest

# Create a Document Intelligence client class 
class DocAnalysisClient:

    def __init__(self):
        self.key = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")
        self.endpoint = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")

        self.document_analysis_client = DocumentIntelligenceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )
        

    def analyze_document(self, document: str) -> str:
        pass

    def analyze_image(self, image: str, question: str) -> str:
        pass

    def analyze_invoice(self, document: str) -> str:
        pass

    def analyze_invoice_from_path(self, document_path: str) -> str:

        # helper functions

        def get_words(page, line):
            result = []
            for word in page.words:
                if _in_span(word, line.spans):
                    result.append(word)
            return result


        def _in_span(word, spans):
            for span in spans:
                if word.span.offset >= span.offset and (
                    word.span.offset + word.span.length
                ) <= (span.offset + span.length):
                    return True
            return False

        document_data = open(document_path, "rb").read()
        b64_encoded_doc = base64.b64encode(document_data).decode('ascii')

        # [START analyze_invoices]

        analyze_request = AnalyzeDocumentRequest(
            
            # url_source=formUrl,
            bytes_source=b64_encoded_doc
        )
        with open(document_path, "rb") as f:
            poller = self.document_analysis_client.begin_analyze_document(
                "prebuilt-invoice", analyze_request=f, content_type="application/octet-stream"
            )
            
        result: AnalyzeResult = poller.result()
        if result.styles and any([style.is_handwritten for style in result.styles]):
            print("Document contains handwritten content")
        else:
            print("Document does not contain handwritten content")

        idx = -1
        for invoice in result.pages:
            idx += 1
            print(f"--------Analyzing invoice #{idx + 1}--------")
            vendor_name = invoice.fields.get("VendorName")
            if vendor_name:
                print(
                    f"Vendor Name: {vendor_name.value} has confidence: {vendor_name.confidence}"
                )
            vendor_address = invoice.fields.get("VendorAddress")
            if vendor_address:
                print(
                    f"Vendor Address: {vendor_address.value} has confidence: {vendor_address.confidence}"
                )
            vendor_address_recipient = invoice.fields.get("VendorAddressRecipient")
            if vendor_address_recipient:
                print(
                    f"Vendor Address Recipient: {vendor_address_recipient.value} has confidence: {vendor_address_recipient.confidence}"
                )
            customer_name = invoice.fields.get("CustomerName")
            if customer_name:
                print(
                    f"Customer Name: {customer_name.value} has confidence: {customer_name.confidence}"
                )
            customer_id = invoice.fields.get("CustomerId")
            if customer_id:
                print(
                    f"Customer Id: {customer_id.value} has confidence: {customer_id.confidence}"
                )
            customer_address = invoice.fields.get("CustomerAddress")
            if customer_address:
                print(
                    f"Customer Address: {customer_address.value} has confidence: {customer_address.confidence}"
                )
            customer_address_recipient = invoice.fields.get("CustomerAddressRecipient")
            if customer_address_recipient:
                print(
                    f"Customer Address Recipient: {customer_address_recipient.value} has confidence: {customer_address_recipient.confidence}"
                )
            invoice_id = invoice.fields.get("InvoiceId")
            if invoice_id:
                print(
                    f"Invoice Id: {invoice_id.value} has confidence: {invoice_id.confidence}"
                )
            invoice_date = invoice.fields.get("InvoiceDate")
            if invoice_date:
                print(
                    f"Invoice Date: {invoice_date.value} has confidence: {invoice_date.confidence}"
                )
            invoice_total = invoice.fields.get("InvoiceTotal")
            if invoice_total:
                print(
                    f"Invoice Total: {invoice_total.value} has confidence: {invoice_total.confidence}"
                )
            due_date = invoice.fields.get("DueDate")
            if due_date:
                print(f"Due Date: {due_date.value} has confidence: {due_date.confidence}")
            purchase_order = invoice.fields.get("PurchaseOrder")
            if purchase_order:
                print(
                    f"Purchase Order: {purchase_order.value} has confidence: {purchase_order.confidence}"
                )
            billing_address = invoice.fields.get("BillingAddress")
            if billing_address:
                print(
                    f"Billing Address: {billing_address.value} has confidence: {billing_address.confidence}"
                )
            billing_address_recipient = invoice.fields.get("BillingAddressRecipient")
            if billing_address_recipient:
                print(
                    f"Billing Address Recipient: {billing_address_recipient.value} has confidence: {billing_address_recipient.confidence}"
                )
            shipping_address = invoice.fields.get("ShippingAddress")
            if shipping_address:
                print(
                    f"Shipping Address: {shipping_address.value} has confidence: {shipping_address.confidence}"
                )
            shipping_address_recipient = invoice.fields.get("ShippingAddressRecipient")
            if shipping_address_recipient:
                print(
                    f"Shipping Address Recipient: {shipping_address_recipient.value} has confidence: {shipping_address_recipient.confidence}"
                )
            print(f"Invoice fields: {invoice.fields.keys()}")
            print("Invoice items:")
            for idx, item in enumerate(invoice.fields.get("Items").value):
                print(f"...Item #{idx + 1}")
                item_description = item.value.get("Description")
                if item_description:
                    print(
                        f"......Description: {item_description.value} has confidence: {item_description.confidence}"
                    )
                item_quantity = item.value.get("Quantity")
                if item_quantity:
                    print(
                        f"......Quantity: {item_quantity.value} has confidence: {item_quantity.confidence}"
                    )
                unit = item.value.get("Unit")
                if unit:
                    print(f"......Unit: {unit.value} has confidence: {unit.confidence}")
                unit_price = item.value.get("UnitPrice")
                if unit_price:
                    unit_price_code = unit_price.value.code if unit_price.value.code else ""
                    print(
                        f"......Unit Price: {unit_price.value}{unit_price_code} has confidence: {unit_price.confidence}"
                    )
                product_code = item.value.get("ProductCode")
                if product_code:
                    print(
                        f"......Product Code: {product_code.value} has confidence: {product_code.confidence}"
                    )
                item_date = item.value.get("Date")
                if item_date:
                    print(
                        f"......Date: {item_date.value} has confidence: {item_date.confidence}"
                    )
                tax = item.value.get("Tax")
                if tax:
                    print(f"......Tax: {tax.value} has confidence: {tax.confidence}")
                amount = item.value.get("Amount")
                if amount:
                    print(
                        f"......Amount: {amount.value} has confidence: {amount.confidence}"
                    )
            subtotal = invoice.fields.get("SubTotal")
            if subtotal:
                print(f"Subtotal: {subtotal.value} has confidence: {subtotal.confidence}")
            total_tax = invoice.fields.get("TotalTax")
            if total_tax:
                print(
                    f"Total Tax: {total_tax.value} has confidence: {total_tax.confidence}"
                )
            previous_unpaid_balance = invoice.fields.get("PreviousUnpaidBalance")
            if previous_unpaid_balance:
                print(
                    f"Previous Unpaid Balance: {previous_unpaid_balance.value} has confidence: {previous_unpaid_balance.confidence}"
                )
            amount_due = invoice.fields.get("AmountDue")
            if amount_due:
                print(
                    f"Amount Due: {amount_due.value} has confidence: {amount_due.confidence}"
                )
            service_start_date = invoice.fields.get("ServiceStartDate")
            if service_start_date:
                print(
                    f"Service Start Date: {service_start_date.value} has confidence: {service_start_date.confidence}"
                )
            service_end_date = invoice.fields.get("ServiceEndDate")
            if service_end_date:
                print(
                    f"Service End Date: {service_end_date.value} has confidence: {service_end_date.confidence}"
                )
            service_address = invoice.fields.get("ServiceAddress")
            if service_address:
                print(
                    f"Service Address: {service_address.value} has confidence: {service_address.confidence}"
                )
            service_address_recipient = invoice.fields.get("ServiceAddressRecipient")
            if service_address_recipient:
                print(
                    f"Service Address Recipient: {service_address_recipient.value} has confidence: {service_address_recipient.confidence}"
                )
            remittance_address = invoice.fields.get("RemittanceAddress")
            if remittance_address:
                print(
                    f"Remittance Address: {remittance_address.value} has confidence: {remittance_address.confidence}"
                )
            remittance_address_recipient = invoice.fields.get("RemittanceAddressRecipient")
            if remittance_address_recipient:
                print(
                    f"Remittance Address Recipient: {remittance_address_recipient.value} has confidence: {remittance_address_recipient.confidence}"
                )
        # [END analyze_invoices]


if __name__ == "__main__":

    try:
        env_name = os.getenv("ENV_NAME", "local")
        env_file_path = Path(f"../.env.{env_name}")
        print(f"Loading environment from: {env_file_path}")
        with open(env_file_path) as f:
            dotenv.load_dotenv(dotenv_path=env_file_path)

        doc_analysis_client = DocAnalysisClient()
        doc_analysis_client.analyze_invoice_from_path("./Invoice 4.pdf")

    except HttpResponseError as error:
        print(
            "For more information about troubleshooting errors, see the following guide: "
            "https://aka.ms/azsdk/python/formrecognizer/troubleshooting"
        )
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise