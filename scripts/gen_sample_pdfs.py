"""Generate the three sample PDFs in samples/docs/ with fpdf2.

Run once (the PDFs are committed):
    python scripts/gen_sample_pdfs.py

Content is original public-domain-style sample text. Each page is a fixed
list of (heading, paragraph) blocks so samples/gold.jsonl can point at exact
doc + page pairs.
"""

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "samples" / "docs"

# filename -> list of pages -> list of (heading, paragraph) blocks
DOCS: dict[str, list[list[tuple[str, str]]]] = {
    "store_policy_manual.pdf": [
        [  # page 1
            (
                "Northwind Home Goods Store Policy Manual",
                "This manual describes the customer-facing policies of Northwind Home Goods. "
                "It covers returns, refunds, shipping, payments, gift cards, price matching and "
                "the loyalty program. Store associates should treat this document as the single "
                "source of truth when answering customer questions.",
            ),
            (
                "Returns and Refunds",
                "The standard return window is 30 days from the date of delivery. Items must be "
                "unused and in their original packaging with proof of purchase. Refunds are issued "
                "to the original payment method within 5 business days of receiving the returned "
                "item. Clearance items marked as final sale cannot be returned.",
            ),
            (
                "Damaged or Defective Items",
                "If an item arrives damaged or defective, contact customer service within 7 days "
                "of delivery with a photo of the damage. We will send a prepaid return label and "
                "issue a full refund or a free replacement, including the original shipping cost. "
                "Damaged items do not need to be in original packaging.",
            ),
        ],
        [  # page 2
            (
                "Shipping Policy",
                "Standard shipping takes 5 to 7 business days and is free on orders above 50 "
                "dollars. Express shipping takes 2 business days and costs 12 dollars. Orders "
                "placed before 2 PM local time ship the same day. We currently ship only within "
                "the continental United States.",
            ),
            (
                "Payment Methods",
                "We accept Visa, Mastercard, American Express, PayPal and Northwind gift cards. "
                "We do not accept personal checks or cash on delivery. Payment is captured when "
                "the order ships, not when it is placed. Sales tax is calculated at checkout "
                "based on the delivery address.",
            ),
        ],
        [  # page 3
            (
                "Price Matching",
                "Northwind offers price matching against major online retailers. If you find an "
                "identical in-stock item at a lower advertised price within 14 days of purchase, "
                "we refund the difference. Price matching does not apply to marketplace sellers, "
                "flash sales or clearance events.",
            ),
            (
                "Gift Cards",
                "Gift cards are available in amounts from 10 to 500 dollars and never expire. "
                "They can be redeemed online or in any store and cannot be exchanged for cash. "
                "Lost gift cards can be replaced with the original receipt for the unused "
                "balance.",
            ),
        ],
        [  # page 4
            (
                "Loyalty Program",
                "Members of the Northwind Rewards loyalty program earn 1 point for every dollar "
                "spent. Every 100 points converts into a 5 dollar reward certificate. Points are "
                "credited 24 hours after delivery and expire after 12 months of account "
                "inactivity. Membership is free and can be cancelled at any time.",
            ),
            (
                "Privacy of Customer Data",
                "Northwind collects only the data needed to process orders and never sells "
                "customer information to third parties. Customers can request deletion of their "
                "account data at any time by contacting privacy@northwind.example.",
            ),
        ],
    ],
    "aurora_kettle_manual.pdf": [
        [  # page 1
            (
                "Aurora AK-200 Electric Kettle User Manual",
                "Thank you for choosing the Aurora AK-200 variable temperature electric kettle. "
                "Read this manual completely before first use and keep it for future reference. "
                "This manual covers setup, daily operation, descaling, troubleshooting and the "
                "technical specifications of the appliance.",
            ),
            (
                "Important Safety Instructions",
                "Use the kettle only with the supplied power base. Do not immerse the kettle, "
                "base or cord in water. Keep the appliance out of reach of children while hot. "
                "Do not operate the kettle when it is empty, and unplug it before cleaning. Use "
                "only on a dry, flat and heat resistant surface.",
            ),
        ],
        [  # page 2
            (
                "Getting Started",
                "Before first use, fill the kettle to the MAX line, boil the water and discard "
                "it twice to remove any manufacturing residue. Place the power base on a flat "
                "surface and wind excess cord into the storage recess under the base. The kettle "
                "switches off automatically when the selected temperature is reached.",
            ),
            (
                "Selecting the Water Temperature",
                "Press the TEMP button to select the water temperature. Five presets are "
                "available: 60, 70, 80, 90 and 100 degrees Celsius. Green tea is best at 80 "
                "degrees, coffee at 90 degrees, and black tea at a full boil of 100 degrees. The "
                "HOLD button keeps the selected temperature for 30 minutes.",
            ),
        ],
        [  # page 3
            (
                "Descaling and Maintenance",
                "Descale the kettle every 4 to 6 weeks in hard water areas. Fill the kettle with "
                "a mixture of half water and half white vinegar, boil once, then let it stand "
                "for 30 minutes before rinsing thoroughly three times. Never use abrasive "
                "cleaners on the stainless steel body. Wipe the outside with a soft damp cloth "
                "only.",
            ),
            (
                "Troubleshooting",
                "If the kettle does not turn on, check that the power base is plugged in and "
                "that the kettle sits fully seated on the base. If the kettle switches off "
                "before boiling, it most likely needs descaling. If the boil-dry protection has "
                "triggered, let the kettle cool for 10 minutes before using it again.",
            ),
        ],
        [  # page 4
            (
                "Technical Specifications",
                "The Aurora AK-200 has a capacity of 1.7 liters and a 2200 watt concealed "
                "heating element. It operates on 220 to 240 volts at 50 to 60 hertz. The body "
                "is brushed stainless steel with a BPA-free water window, and the kettle weighs "
                "1.2 kilograms without the base.",
            ),
            (
                "Warranty",
                "The Aurora AK-200 is covered by a 2 year limited warranty from the date of "
                "purchase. The warranty covers manufacturing defects but not damage caused by "
                "limescale, misuse or unauthorized repair. Register your kettle at "
                "aurora.example/register within 30 days to activate the warranty.",
            ),
        ],
    ],
    "service_contract_template.pdf": [
        [  # page 1
            (
                "Master Service Agreement Template",
                "This Master Service Agreement, hereafter the Agreement, is entered into between "
                "the Client and the Contractor identified on the signature page. It sets out the "
                "general terms under which the Contractor provides services described in one or "
                "more attached Statements of Work.",
            ),
            (
                "Definitions",
                "Services means the work described in a Statement of Work. Deliverables means "
                "the work products to be provided to the Client. Confidential Information means "
                "any non-public information disclosed by either party in connection with this "
                "Agreement, whether marked confidential or not.",
            ),
        ],
        [  # page 2
            (
                "Scope of Services",
                "The Contractor shall perform the Services described in each Statement of Work "
                "with reasonable skill and care. Changes to scope must be agreed in writing "
                "through a change order signed by both parties. The Contractor may not "
                "subcontract the Services without prior written consent of the Client.",
            ),
            (
                "Payment Terms",
                "The Client shall pay each undisputed invoice within 30 days of receipt, known "
                "as net 30 payment terms. Late payments accrue a late fee of 1.5 percent per "
                "month on the outstanding balance. The Contractor may suspend the Services if an "
                "undisputed invoice remains unpaid for more than 60 days.",
            ),
        ],
        [  # page 3
            (
                "Confidentiality",
                "Each party shall protect the other party's Confidential Information with the "
                "same care it uses for its own, and no less than reasonable care. Confidential "
                "Information may be used only to perform this Agreement and may not be disclosed "
                "to third parties for a period of 3 years after termination.",
            ),
            (
                "Termination",
                "Either party may terminate this Agreement for convenience with 30 days written "
                "notice to the other party. Either party may terminate immediately if the other "
                "party materially breaches the Agreement and fails to cure the breach within 15 "
                "days of written notice. Upon termination the Client pays for all Services "
                "performed to date.",
            ),
        ],
        [  # page 4
            (
                "Limitation of Liability",
                "Neither party is liable for indirect, incidental or consequential damages. The "
                "total liability of either party under this Agreement is capped at the fees paid "
                "by the Client in the 12 months preceding the claim. Nothing in this clause "
                "limits liability for gross negligence or willful misconduct.",
            ),
            (
                "Governing Law",
                "This Agreement is governed by the laws of the State of Delaware, without regard "
                "to its conflict of law rules. Any dispute arising from this Agreement shall be "
                "resolved in the state or federal courts located in Delaware, and both parties "
                "consent to that jurisdiction.",
            ),
        ],
    ],
}


def build_pdf(pages: list[list[tuple[str, str]]], path: Path) -> None:
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=False)
    for blocks in pages:
        pdf.add_page()
        y = 20
        for heading, paragraph in blocks:
            pdf.set_xy(20, y)
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(170, 8, heading)
            pdf.set_x(20)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(170, 6, paragraph)
            y = pdf.get_y() + 8
    pdf.output(str(path))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, pages in DOCS.items():
        path = OUT / filename
        build_pdf(pages, path)
        print(f"wrote {path} ({len(pages)} pages)")


if __name__ == "__main__":
    main()
