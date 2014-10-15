import module
# unique to module
from BeautifulSoup import BeautifulSoup

class Module(module.Module):

    def __init__(self, params):
        module.Module.__init__(self, params, query='SELECT first_name,last_name,region FROM contacts WHERE last_name IS NOT NULL and country ="United Kingdom" ORDER BY last_name')
        try:
            self.query('ALTER TABLE contacts ADD COLUMN address TEXT')
            self.query('ALTER TABLE contacts ADD COLUMN phone_number TEXT')
        except:
            pass
        self.info = {
            'Name': 'BT Lookup',
            'Author': 'Adam Maxwell (@catalyst265) and Sam Brown (@samdb)',
            'Description': """Harvests phone numbers and addresses for UK contacts from the 
            BT Phonebook website. Updates the \'contacts\' table with the results."""
        }

    def module_run(self, contacts):
        self.updated_count = 0
        for person in contacts:
            url = 'http://www.thephonebook.bt.com/publisha.content/en/search/residential/search.publisha'
            first_name,last_name,region = person
            first_initial = first_name[0]
            payload = {'Surname':last_name,
                        'Location':region,
                        'Initial':first_initial,
                        'Street':''
                       }
            resp = self.request(url,payload=payload)
            parsed_html = BeautifulSoup(resp.text)
            x = parsed_html.body.findAll('div', attrs={'class':'recordBody'})
            parsed_results = []
            for result in x:
                lookup_result = result.text.replace('Tel: (', ',').replace(')', '').replace('-Text Number', ',').replace('-Map', '').split(',')
                names = lookup_result[0].split(' ')
                #Only some results have full first names - if a result does a full first name make sure 
                #it matches the first_name that we have for the contact
                if len(names[0]) == 1 or (len(names[0]) > 1 and names[0] == first_name):
                    parsed_results.append(lookup_result)
            #if no results skip on to next person
            if len(parsed_results) == 0:
                continue
            #if only one result, assume its who we want
            if len(parsed_results) == 1:
                self.update_contacts(first_name,last_name,region,parsed_results[0])
            else:
                self.output("Choose option (enter non-integer to skip) to set phone_number and address of %s %s who lives in region: %s to:" % (first_name,last_name,region))
                for i,s in enumerate(parsed_results):
                    phone_number = s[1]
                    address = ','.join(s[2:])
                    self.output("%d: phone_number: %s and address: %s" % (i,phone_number,address))
                while True:
                    choice = raw_input()
                    try:
                        choice = int(choice)
                        try:
                            chosen = parsed_results[choice]
                            self.update_contacts(first_name,last_name,region,chosen)
                            break
                        except:
                            self.output('Invalid choice please re-enter:')
                    except:
                        break
        self.output('Added details for %d contact records.' % self.updated_count)     

    def update_contacts(self,first_name,last_name,region,result):
        phone_number = result[1]
        address = ','.join(result[2:])
        self.query('UPDATE contacts SET phone_number=?, address=? WHERE last_name =? AND region=? AND first_name=?',(phone_number,address,last_name,region,first_name))
        self.output('Updated record with first_name: %s , last_name: %s and region: %s to have phone_number: %s and address: %s.' % (first_name, last_name,region,phone_number,address))
        self.updated_count += 1