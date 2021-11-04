import PyWizard
from wizard.core import project



domain_rows = project.get_all_domains()
for domain_row in domain_rows:
    if domain_row['name'] == 'library':
        pass