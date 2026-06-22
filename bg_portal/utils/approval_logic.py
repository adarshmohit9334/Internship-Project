import os

MD_LIMIT = int(os.getenv('MD_APPROVAL_LIMIT', '1500000'))

def get_approval_level(bg_amount: float) -> str:
    return 'MD' if float(bg_amount) <= MD_LIMIT else 'Board'

def validate_attachments(files: dict, approval_level: str) -> list:
    errors = []
    always_required = ['bg_vetted_draft', 'beneficiary_clause', 'bank_account_details']
    for field in always_required:
        if field not in files or not files[field].filename:
            errors.append(f'{field} is required.')
    if approval_level == 'MD':
        if 'md_approval' not in files or not files['md_approval'].filename:
            errors.append('MD Approval document is required for amounts ? ?15,00,000.')
    else:
        if 'board_approval' not in files or not files['board_approval'].filename:
            errors.append('Board Approval document is required for amounts > ?15,00,000.')
    return errors
