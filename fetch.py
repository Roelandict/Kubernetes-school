import os
import yaml
import random
import requests

def change_yaml_names(yaml_content):
    """
    Parses YAML content, changes pod and container names with a random 8-digit ID,
    and returns the modified YAML content.
    """
    # Generate a random 8-digit ID
    new_id = str(random.randint(10000000, 99999999))
    
    # Load all YAML documents from the string
    documents = yaml.safe_load_all(yaml_content)
    
    modified_docs = []
    
    for doc in documents:
        if doc and 'kind' in doc and doc['kind'] == 'Pod':
            # Check for the existence of nested keys before accessing
            if 'metadata' in doc and 'name' in doc['metadata']:
                pod_name = doc['metadata']['name']
                doc['metadata']['name'] = f"{pod_name}-{new_id}"

            if 'spec' in doc and 'containers' in doc['spec'] and doc['spec']['containers']:
                container_name = doc['spec']['containers'][0]['name']
                doc['spec']['containers'][0]['name'] = f"{container_name}-{new_id}"
        if doc and 'kind' in doc and doc['kind'] == 'Service':
            if 'metadata' in doc and 'name' in doc['metadata']:
                service_name = doc['metadata']['name']
                doc['metadata']['name'] = f"{service_name}-{new_id}"

        modified_docs.append(doc)
    
    # Dump the modified documents back to a YAML string
    modified_yaml = yaml.safe_dump_all(modified_docs, sort_keys=False)
    
    filePath = f"deploy-nginx-{new_id}.yaml"
    with open(filePath, 'w') as f:
        f.write(modified_yaml)
    
    return modified_yaml, filePath # Return both the yaml string and the file path

# The URL to the raw YAML file on GitHub
yaml_url = "https://raw.githubusercontent.com/Roelandict/Kubernetes-school/main/scripts/pods/nginx.yml"

try:
    # Fetch the raw YAML content from the URL
    response = requests.get(yaml_url)
    
    # Raise an exception for bad status codes (4xx or 5xx)
    response.raise_for_status() 
    
    # The content of the YAML file is in response.text
    yaml_string = response.text
    
    # Call the function with the fetched YAML content
    new_yaml_string, file_path_for_creation = change_yaml_names(yaml_string)

    # Print the modified YAML
    print(new_yaml_string)
    
    # Create the Kubernetes resource using the newly created YAML file
    print(f"Applying Kubernetes configuration from {file_path_for_creation}...")
    os.system(f"kubectl create -f {file_path_for_creation} -n test")

except requests.exceptions.RequestException as e:
    # Handle any errors that occur during the request
    print(f"An error occurred: {e}")
    exit(1)