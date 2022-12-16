import os, shutil, re, json

# Template for the exported section JSON object
section_template = {
    "name": "",
    "description": "",
    "id": 0,
    "usage": ""
}

# Output markdown template
export_template = """
<details>

<summary>/<mark style="color:orange;">{name}</mark></summary>

{description}

{usage}

ID# {id}

</details>
"""

def create_section(section_data):
    section_parts = [each.split('\n\n') for each in section_data]
    section_object = section_template.copy()
    section_object['name'] = section_parts[0][0]
    section_object['description'] = section_parts[0][1]
    section_object['id'] = section_parts[1][1]
    section_object['usage'] = section_parts[2][1].replace('\b', '').replace('\n', '')
    return section_object

def splitter(md_raw):
    page = {}
    sections = md_raw.split('\n## ')
    page['heading'] = sections[0]
    sections = [ea.split('###') for ea in sections[1:]]
    page['sections'] = []
    for sect in sections:
        page['sections'].append(create_section(sect))
    return page

def loader(filename):
    if os.path.isfile(os.path.realpath(filename)):
        with open(os.path.realpath(filename), 'r') as fp:
            return splitter(fp.read())
    else:
        raise ValueError(f'The specified file could not be located: {filename}')
    

def writer(data, filename):
    fn = filename.replace('.md', '.json')
    print(f'Outputting to {fn}...')
    with open(fn, 'w') as fp:
        fp.write(json.dumps(data, indent=4))
        print(f'Wrote JSON to {fn}')
    return fn

def converter(fn):
    jsondata = {}
    outputdata = []
    if not os.path.isdir('converted'):
        os.mkdir('converted')
    with open(fn, 'r') as fp:
        jsondata = json.loads(fp.read())
    outputdata.append(jsondata['heading'])
    for each in jsondata['sections']:
        outputdata.append(export_template.format(name=each['name'], description=each['description'], id=each['id'], usage=each['usage']))
    with open(f"converted/{os.path.basename(fn.replace('.json', '.new.md'))}", 'w') as fd:
        fd.write('\n'.join(outputdata))

def main_format_json():
    files = []
    if 'commands' in os.listdir(os.getcwd()) and os.path.isdir('commands'):
        files = [os.path.realpath(f'commands/{file}') for file in os.listdir('commands') if 'core.md' not in file and file.endswith('.md')]
    elif len([each for each in os.listdir(os.getcwd()) if each.endswith('md')]) > 0:
        files = [file for file in os.listdir(os.getcwd()) if 'core.md' not in file and file.endswith('.md')]
    if len(files) == 0:
        print("Runtime error: No suitable files found.")
    for each in files:
        try:
            print(f"Processing {each}", end=" ")
            data = loader(each)
            print("Loaded data. ")
            print("Writing json. ")
            newfn = writer(data, each)
            print("Wrote json.", newfn)
            converter(newfn)
            print(f"Processing {each} complete")
        except Exception as e:
            print(f"An error occurred processing {each}:\n", e)

if __name__ == "__main__":
    try:
        main_format_json()
        print("Operation completed successfully.")
    except Exception as e:
        print("An error occurred: ", e)