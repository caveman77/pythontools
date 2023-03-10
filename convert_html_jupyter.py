from bs4 import BeautifulSoup
#from beautifulsoup4 import BeautifulSoup
import json
import urllib
import re




def parse_cell_output(div):
        cell = {} 
        cell['output_type'] = "stream"
        cell['name'] = "stdout"      
        cell['text'] = []
        
        
        #print('find level 1')
        for div2 in div.find_all('pre'):
            #line = {}
            ligneavecbalises = div2.get_text()
            ligne = ligneavecbalises
            #ligne = re.sub('<.*?>', '', ligneavecbalises)

            ligne = ligne.replace(u'\u200b', '\n')
            ligne = ligne.replace(u'\u0d0a', '\n')


            if ligne != '' :
                #lignehex = ":".join("{:02x}".format(ord(c)) for c in ligne)
                #print(ligne, lignehex)
                
                #cell['source'].append(json.dumps(ligne))
                cell['text'].append(ligne)

        return cell


def parse_cell_outputPng(div):
        cell = {} 
        cell['data'] = { }
        
        
        #text_html = []
        
        for item in div.contents:
            txt = str(item)
            txt = txt.replace('\n', '')
            
            paterns = re.findall('base64,.*?\"',  txt)
            for pat in paterns:
                #print("Found 1 img")
                ligne = pat[7:-1]

                if ligne != '' :
                    #lignehex = ":".join("{:02x}".format(ord(c)) for c in ligne)
                    #print(ligne)
                    
                    #cell['source'].append(json.dumps(ligne))
                    text_html = ligne
                    #print(ligne)
                    cell['data']["image/png"] = text_html

        return cell


def parse_cell_outputHtml(div):
        cell = {} 
        cell['output_type'] = "execute_result"
        cell['data'] = { }
        
        
        text_html = []
        for item in div.contents:
            txt = str(item)
            
            #print('ligneavecbalises:', txt)
            ligne = txt

            if ligne != '' :
                #lignehex = ":".join("{:02x}".format(ord(c)) for c in ligne)
                #print(ligne)
                
                #cell['source'].append(json.dumps(ligne))
                text_html.append(ligne)

        
        cell['data']["text/html"] = text_html


        return cell

def parse_cell_Exec(div):
    txt = str(div)

    try:
        patern = re.findall('\[.*?\]',  txt)
        num = int(patern[0][1:-1])
        return num

    except ValueError:
        return -1



def parse_cell_code(div, cell_back_ground_wellow):

        source = []
        
        if cell_back_ground_wellow:
            source.append('#SOL:\n')

        #print('find level 1')
        for div2 in div.find_all('pre', attrs={'class': 'CodeMirror-line'}):
            #line = {}
            ligneavecbalises = div2.get_text()
            ligne = re.sub('<.*?>', '', ligneavecbalises)

            ligne = ligne.replace(u'\u200b', '\n')
            ligne = ligne.replace(u'\u0d0a', '\n')


            if ligne != '' :
                #lignehex = ":".join("{:02x}".format(ord(c)) for c in ligne)
                #print(ligne, lignehex)
                
                #cell['source'].append(json.dumps(ligne))
                ligne = ligne + '\n'
                source.append(ligne)

        return source

def parse_cell_inout(div, DownloadCode,  DownloadOutput):
        cell = {} 
        cell['metadata'] = {}
        cell['cell_type'] = "code"
        cell['execution_count'] = None      
        cell['outputs'] = []
        cell['source'] = []

        cell_back_ground_wellow = False
        
        for div2 in div.find_all('div', attrs={'class': ['input_area', 'output_subarea', 'input_prompt' ]}):
            #print(div['aria-label'])
            #if 'input_area' in div2['class'] and div2['aria-label']=='Edit code here':
            if 'input_area' in div2['class'] and DownloadCode==True:
                #print('In Out detected')

                try:
                    if div2['style']=="background-color: rgb(255, 254, 240);":
                        cell_back_ground_wellow= True
                        cell['metadata']['function'] = "Yellow"
                except KeyError:
                    pass

                onecell = parse_cell_code(div2, cell_back_ground_wellow)
                #cell['source'].append(onecell)
                cell['source'] = onecell
            else:
                if 'output_subarea' in div2['class'] and 'output_text' in div2['class'] and DownloadOutput==True:
                    #print('Text Ouput detected')
                    onecellout = parse_cell_output(div2)
                    cell['outputs'].append(onecellout)

                if 'output_subarea' in div2['class'] and 'output_html' in div2['class'] and DownloadOutput==True:
                    #print('Html Ouput detected')
                    onecellout = parse_cell_outputHtml(div2)
                    cell['outputs'].append(onecellout)

                if 'output_subarea' in div2['class'] and 'output_png' in div2['class'] and DownloadOutput==True:
                    #print('Png Ouput detected')
                    onecellout = parse_cell_outputPng(div2)
                    cell['outputs'].append(onecellout)

                if 'input_prompt' in div2['class'] and DownloadOutput==True:
                    #print('Excecution count detected')
                    onecellout = parse_cell_Exec(div2)

                    if onecellout != -1:
                        cell['execution_count'] = onecellout

        return cell

def parse_cell_markup(div):
        cell = {} 
        cell['metadata'] = {}
        cell['cell_type'] = "markdown"
        cell['source'] = []
        
        
        for item in div.contents:
            txt = str(item)
            
            #print('ligneavecbalises:', txt)
            ligne = re.sub('<blockquote.*?>', '> ', txt)
            ligne = re.sub('</blockquote>', '\n', ligne)
            ligne = re.sub('#', '\#', ligne)
            
            ligne = re.sub('<li>', '* ', ligne)
            ligne = re.sub('</?strong>', '**', ligne)
            ligne = re.sub('<h[1-9].*?>', '# ', ligne)
            
        
            ligne = re.sub('<.*?>', '', ligne)

            ligne = ligne.replace(u'\u200b', '\n')


            if ligne != '' :
                #lignehex = ":".join("{:02x}".format(ord(c)) for c in ligne)
                #print(ligne)
                
                #cell['source'].append(json.dumps(ligne))
                cell['source'].append(ligne)

        return cell
        
def get_data(soup, DownloadMarkup, DownloadCode,  DownloadOutput):
    create_nb = {}  

    create_nb['nbformat'] = 4
    create_nb['nbformat_minor'] = 2
    create_nb['cells'] = []
    create_nb['metadata'] = {"kernelspec": 
              {"display_name": "Python 3", 
               "language": "python", "name": "python3"  }}
 
    # Loop on cells (input only)
    for div in soup.find_all('div', attrs={'class': ['code_cell', 'text_cell_render' ]}):
        #print(div['aria-label'])
        if 'code_cell' in div['class']:
            #print('In Out detected')
            cell = parse_cell_inout(div, DownloadCode,  DownloadOutput)
            create_nb['cells'].append(cell)
        else:
            if 'text_cell_render' in div['class'] and DownloadMarkup==True:
                #print('Markup detected')
                cell = parse_cell_markup(div)
                create_nb['cells'].append(cell)

                

        print('.', end='')

    print('.')    
    return create_nb








import sys


DownloadMarkup=True
DownloadCode=True
DownloadOutput=True

filelist=[]
for i, arg in enumerate(sys.argv):
    
    if i>0:
        if len(arg) >=2 and arg[0] == '-':
            param=True      

            if arg[2] == '0' or arg[2] == '0':
                param=False

            if arg[1] == 'm' or arg[1] == 'M':
                DownloadMarkup=param
                print('Switching markup to:', DownloadMarkup)

            elif arg[1] == 'c' or arg[1] == 'C':
                DownloadCode=param
                print('Switching code to:', DownloadCode)

            elif arg[1] == 'o' or arg[1] == 'O':
                DownloadOutput=param
                print('Switching output to:', DownloadOutput)
        else:
            filelist.append(arg)


for   filenamearg in     filelist: 
    with open(filenamearg) as filenames:
        #print(filenames.name)

        print("managing ", filenames.name)
        fhand = open(filenames.name, mode="r", encoding="utf-8")
        text = fhand.read()

        #print('Please wait')
        soup = BeautifulSoup(text, 'lxml')

        #get_data(soup, 'post-content')
        create_nb = get_data(soup, DownloadMarkup, DownloadCode,  DownloadOutput)

        #print('Saving outcome')
        with open(filenames.name + '.ipynb', 'w') as jynotebook:
            jynotebook.write(json.dumps(create_nb))



