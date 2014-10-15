import module
# unique to module
from BeautifulSoup import BeautifulSoup

class Module(module.Module):

    def __init__(self, params):
        module.Module.__init__(self, params, query='SELECT last_name,first_name,region FROM contacts WHERE last_name IS NOT NULL and country ="United Kingdom" ORDER BY last_name')
        self.info = {
                     'Name': 'BT Lookup',
                     'Author': 'Adam Maxwell (@catalyst265) and Sam Brown (@samdb)',
                     'Description': 'Harvests contacts from Facebook.com. Updates the \'contacts\' table with the results.',
                     }

    def module_run(self, details):
        count = 0
        for person in details:
            url = 'http://www.thephonebook.bt.com/publisha.content/en/search/residential/search.publisha'
            surname = person[0]
            location = person[2]
            first_name = person[1]
            first_initial = first_name[0]
            payload = {'Surname':surname,
                        'Location':location,
                        'Initial':first_initial,
                        'Street':''
                       }
            resp = self.request(url,payload=payload)
            parsed_html = BeautifulSoup(resp.text)
            x = parsed_html.body.findAll('div', attrs={'class':'recordBody'})
            if len(x) > 0:
                try:
                    self.query('ALTER TABLE contacts ADD COLUMN address TEXT')
                    self.query('ALTER TABLE contacts ADD COLUMN phone_number TEXT')
                except:
                    #already added...should probably make this more eloquent...
                    pass
            if len(x) == 1:
                wut = s.text.replace('Tel: (', ',').replace(')', '').replace('-Text Number', ',').replace('-Map', '').split(',')
                phone_number = wut[1]
                address = wut[2] + ',' + wut[3] + ',' + wut[4]
                self.output("Updated contact with first_name:%s, last_name:%s and region: %s to have phone_number:%s and address:%s")
                self.query('UPDATE contacts SET phone_number=?, address=? WHERE last_name =? AND region=? AND first_name LIKE ?',(phone_number,address,surname,location,first_initial +'%'))
            else:
                self.output("Choose option (enter non-integer to skip) to set phone_number and address of %s %s who lives in region: %s to:" % (first_name,surname,location))
                for i,s in enumerate(x):
                    wut = s.text.replace('Tel: (', ',').replace(')', '').replace('-Text Number', ',').replace('-Map', '').split(',')
                    names = wut[0].split(' ')
                    if len(names[0]) == 1 or (len(names[0]) > 1 and names[0] == first_name):
                        phone_number = wut[1]
                        address = wut[2] + ',' + wut[3] + ',' + wut[4]
                        self.output("%d: phone_number:%s and address:%s" % (i,phone_number,address))
                while True:
                    choice = raw_input()
                    try:
                        choice = int(choice)
                        try:
                            chosen = x[choice]
                            chosen = chosen.text.replace('Tel: (', ',').replace(')', '').replace('-Text Number', ',').replace('-Map', '').split(',')
                            phone_number = chosen[1]
                            address = chosen[2] + ',' + chosen[3] + ',' + chosen[4]
                            self.query('UPDATE contacts SET phone_number=?, address=? WHERE last_name =? AND region=? AND first_name LIKE ?',(phone_number,address,surname,location,first_initial +'%'))
                            break
                        except:
                            self.output('invalid choice please re-enter:')
                    except:
                        break
        count += 1