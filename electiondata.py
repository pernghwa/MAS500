from bs4 import BeautifulSoup
import requests
import json
import argparse
import re

class ElectionResults(object):
  
    def __init__(self, filename):
        self.filename = filename

    def load(self):
        self.file = open(self.filename, 'r')
        self.all_lines = self.file.readlines()

    def states(self):
        all_names = []
        for line in self.all_lines:
            columns = line.split(',')
            all_names.append(columns[1])
        return all_names[1:]

    def state_count(self):
        return len(self.states())

    def candidates_count(self):
        votes = [0 for i in range((len(self.all_lines[0].split(','))-3)/2)]
        for line in self.all_lines[1:]:
            columns = line.split(',')
            for i in range((len(columns)-3)/2):
                votes[i] += int(columns[3+i*2])      
        return votes

class ElectionResultsWrap(ElectionResults):

    def __init__(self, filename):
        super(ElectionResultsWrap,self).__init__(filename)
        super(ElectionResultsWrap,self).load()
        self.states_vec = super(ElectionResultsWrap,self).states()
        self.state_count = super(ElectionResultsWrap,self).state_count()

    def get_file(self):
        return self.file

    def get_fileData(self):
        return self.all_lines

    def get_states_vec(self):
        return self.states_vec

    def get_state_count(self):
        return self.state_count

class ElectionScrapper:

    def __init__(self, kwarg={'url':None, 'filename':None}):
        self.url = kwarg['url']
        self.filename = kwarg['filename']
        state_file = file("states.csv", "r").readlines()
        self.states = {line.strip().split(',')[0]:line.strip().split(',')[1] for line in state_file}
        self.data = []

    def load_filename(self, filename):
        self.filename = filename

    def load_url(self, url):
        self.url = url

    def scrape_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text)
        rows = soup.find("table").find_all("tr")
        tmp = []

        # Print headers
        row = rows[1].find_all("th")
        # State abbreviation field
        tmp.append(re.sub(r'[^a-zA-Z0-9]',' ',row[0].text))
        # State field
        tmp.append("State_Full")
        # Candidate Vote + % Vote fields
        for c in row[1:-1]:
            term = re.sub(r'[^a-zA-Z0-9]',' ',c.text)
            term = re.sub(r'[\s]+',' ', term)
            tmp.append(term)
            tmp.append("%")

        term = re.sub(r'[^a-zA-Z0-9]',' ',row[-1].text)
        term = re.sub(r'[\s]+',' ', term)
        tmp.append(term)
        self.data.append(tmp)

        for r in rows[2:-1]:
            row = r.find_all("td")
            tmp = []
            st = re.findall(r'[a-zA-Z]+',r.find("th").text)[0]
            tmp.append(st)
            try:
                tmp.append(self.states[st])
            except KeyError:
                tmp.append(' ')
            total = float(row[-1].text)
            for c in row[:-1]:
                try:
                    vote = int(c.text)
                except ValueError:
                    vote = 0
                tmp.append(str(vote))
                tmp.append(str(vote/total))
            tmp.append(str(total))
            self.data.append(tmp)

    def export_json(self):
        columns = []
        for t in range(len(self.data[0])):
            if '%' in self.data[0][t]:
                columns.append(self.data[0][t-1]+" "+self.data[0][t])
            else:
                columns.append(self.data[0][t])
        with file(self.filename, "w") as outFile:
            tmp = {'data':[]}
            for row in self.data[1:]:
                tmp['data'].append(dict([(columns[c], row[c]) for c in range(len(row))]))
            json.dump(tmp, outFile, indent=4)

    def export_csv(self):
        with file(self.filename, "w") as outFile:
            for row in self.data:
                outFile.write(','.join(row)+'\n')

if __name__ == "__main__":
    result_2012 = ElectionResults('2012_US_election_state.csv')
    result_2012.load()
    print result_2012.candidates_count()
    result_2012_wrap = ElectionResultsWrap('2012_US_election_state.csv')
    print result_2012_wrap.candidates_count()
    print result_2012_wrap.get_states_vec()
    print result_2012_wrap.get_state_count()
    scrapper = ElectionScrapper()
    scrapper.load_url("http://www.archives.gov/federal-register/electoral-college/2012/popular-vote.html")
    scrapper.load_filename("election_full_test_file.csv")
    scrapper.scrape_url()
    scrapper.export_csv()
    scrapper.load_filename("election_full_test_file.json")
    scrapper.export_json()