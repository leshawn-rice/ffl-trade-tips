import requests


class News:
    '''
    Class that pulls NFL News from their
    website'''

    def __init__(self):
        self.data = []

    def split_link(self, link):
        '''
        Splits an HTML link into
        a link and a source and returns
        a dict with {'link': link, 'source': source}
        '''
        link_info = {}
        link_data = link.split('(')
        try:
            source_info = link_data[1].strip(')')
            link_info['link'] = link_data[0]
            link_info['source'] = source_info
        except:
            link_info['link'] = link_data[0]
            link_info['source'] = link_data[0]
        return link_info

    def remove_metadata(self, link):
        '''
        Removes unnecessary data from a
        link so we can get just the link
        and the source
        '''
        try:
            para = link.split('</p>')
            heading = para[1].split('</h3>')
            date = heading[1].split('</h3>')[0]
            date += '</h3>'
            link = heading[2].strip('\n')
            return (date, link)
        except:
            try:
                para = link.split('</p>')[0]
                heading = para.split('</h3>')
                date = heading[0].split('</h3>')[0]
                date += '</h3>'
                link = heading[1].strip('\n')
                return (date, link)
            except:
                return (None, link)

    def add_blank_target(self, link_data):
        '''
        Adds target="blank" to a given link
        so it opens in a new page
        '''
        try:
            raw_link = link_data['link'].split('>')
            no_close_link = raw_link[0] + ' target="_blank">'
            no_close_link += raw_link[1] + '>'
            link_data['link'] = no_close_link
        except:
            pass
        return link_data

    def get_news(self):
        '''
        Sends a request to ESPN's NFL news page,
        parses the data, and sets the link into 
        self.data 
        '''
        response = requests.get('http://www.espn.com/espn/wire?sportId=28')
        data = response.text
        data.replace('\n', '<br>')
        data = data.split(
            '<div class="bg-opaque pad-16 article">')[1].split('<br>')
        links = data[0].split(
            '<!-- begin body -->')[1].split('<!-- end body -->')[0]
        links = links.split('<br />')
        for link in links:
            (date, link) = self.remove_metadata(link)
            if date:
                self.data.append({'link': date, 'source': None})
            link_data = self.split_link(link)
            link_data = self.add_blank_target(link_data)
            self.data.append(link_data)
