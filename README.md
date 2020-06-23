# **CI pipeline to train a MNIST dataset-based model with Pytorch**

Implemented with [Github Actions](https://github.com/features/actions)

The CI pipeline will automatically check your pull requests for meeting the Python code style and running end-to-end,
train the full model on a tagged release and upload it to the Azure Blob storage. 
The pipeline stops execution as soon as one of the steps can not be completed.

The process runs on GitHub-hosted machines, called 'runners', on the latest version of `Linux Ubuntu` installed on GitHub runners.
The current version is `ubuntu-18.04`.  You can see the pre-installed software [here](https://github.com/actions/virtual-environments/blob/ubuntu18/20200525.2/images/linux/Ubuntu1804-README.md).

The current configuration of the pipeline runs without errors.
Changes to the workflow `.yml` files and to your code may trigger errors. See below the details of the pipeline, possible errors and how to address them.

## Overview
![GitHub Workflow](/workflow.png)


## Details

### I. Standard steps to set up environment and clean up after the jobs are done:

**1.  Set up job**\
      **does:** sets up the runner, configures the environment, downloads and sets up the actions used in the workflow\
      **fails:** if the requested system or configuration does not exist on the runner or the actions do not exist\
      This can happen if some of the parameters are deprecated, currently not the case.\
      **fix:** request a different system, version, check that the requested actions are available in the Marketplace

**2. Check out the repository**\
      **does:**\
          - checks-out the repository under $GITHUB_WORKSPACE to be accessible in the workflow\
          - uses a prebuilt action checkout@v2. More info here: https://github.com/actions/checkout \
      **fails:** if the action checkout@v2 is no longer accessible.\
      **fix:** check the action in the Marketplace

**3. Set up Python**\
     **does**:\
         - sets up a Python environment\
         - uses the latest available version of Python\
     **fails:** if the requested version of Python is not available\
     **fix**: choose a different version of Python,  check the action here: https://github.com/actions/setup-python

**4. Cache dependencies**\
     **does:**:\
          - speeds up the run by making the dependencies inslalled via pip accessible to the workflow\
          - uses action cache@v2. More info here: https://github.com/actions/cache

**5. Install dependencies**\
    **does:**\
          - runs standard shell commands to install packages\
          - upgrades pip, setuptools and wheel if necessary\
          - installs necessary dependencies from ```requirements.txt``` if specified\
          - uses cache if the installed dependencies are found\
    **fails:** if the requested packages are not compatible with the environment\
    **fix:** check the compatibility and choose different versions of the requested packages
    
 **6. Post-steps for 1, 2, 4**:\
     **does:** saving cache, cleanup, completing the job


### II. Workflows with specific steps:

 #### 1. Test MNIST model
 
   * **triggered:** on any pull request
   * **jobs:** build_and_test
   * **steps:**
 
      * **1 - 5:** Standard steps from I, step 5 additionally:
          - installs ```flake8``` and its dependencies
          - installs ```flake8-docstrings``` extension
          
      * **6. Lint with Flake8**\
           **does:**
           - runs the latest version of flake8 with no parameters
           - checks the python code for meeting the Python code style
           - outputs annotations with where the problem occurred to stdout
           
         **fails:** stops if if there is at least one error - check the errors [here](https://flake8.pycqa.org/en/latest/user/error-codes.html)\
         **fix:** edit the code to meet the standards
    
     * **7. Execute code with minimal train set**\
         **does**:
          - runs the code in ```main.py``` with a flag ```--min_train```
          - the flag stops the iteration over the train loader when the index reaches 10% of the train data\
          - ```main.py:```
                - trains the model on 10% of the train data
                - tests the model on a full test dataset
                - outputs the model into a file specified in the code
                
       **fails:** if unable to execute the code\
       **fix:** follow the error message and debug your code - this is not a CI problem
         
     * **8. Cleanup from I.6**
  
#### 2. Train the full MNIST model and Upload to Azure Blob Storage
  * **triggered:** tagged release
  * **jobs:** build_and_train, upload
  * **steps:**
     * **1 - 5:** Standard steps from I 
        
        ```build_and_train```

      * **6. Execute the code to train the model**\
            **does**: 
           - runs the code in main.py without any flags
           ```main.py:```
           - trains the model on full train data
           - tests the model on a full test dataset
           - outputs the model into a file specified in the code: ```'mnist_model.pth'```
           
           **fails:** if unable to execute the code\
           **fix:** follow the error message and debug your code - this is not a CI problem\
 
      * **7. Create and upload the model artifact**\
           **does**:
           - uses upload-artifact@v2 action. More information: https://github.com/actions/upload-artifact 
           - creates an artifact with the name model_artifact and uploads it to the workspace, which is accessible from Actions
           
           **fails:** if the action is inaccessible, or the path to the file is inaccessible (e.g. you changed the name or the location in the code)\
           **fix:** specify the correct path to the file you want to save as an artifact\
 
      * **8. Cleanup as in I.6.**
 
      ```upload```: relies on the completeness of the previous step

      * **9. Standard setup 1-5**
      
      * **10. Build the action:**\
         **does:**
        - uses Azure Blob Storage Upload action from the Marketplace. More info: https://github.com/marketplace/actions/azure-blob-storage-upload

      * **11. Download the model artifact**\
          **does:**
        - runs action download-artifact@v1. More information: https://github.com/actions/download-artifact
        - creates a folder with the specified model file in the workspace - this step is necessary for making the file available to the subsequent actions
        
         **fails**: if the artifact does not exist - wrong name or path\
         **fix:** check the name of the artifact

      * **12. Upload to Azure Blob**\
          **does:**
        - run bacongobbler/azure-blob-storage-upload@v1.1.1 action
        - establishes the connection with the specified Azure container
        - uploads the specified model file to Azure Blob Storage with specified credentials
        
         **fails**: if the action is not accessible or the credentials are wrong\
         **fix:** check the azure credentials and modify the connection string with new credentials
      * **13. Standard cleanup**

## Troubleshooting and Modifications

The files describing the workflow are stored in ```.github/workflows.```
The files use YAML syntax and have `.yml` file extension. If the `.yml` files contain syntax errors, the corresponding workflow will break without execution.

If you encountered any of the errors described above concerning the CI pipeline, it is likely an easy fix to one of the .`yml` files. Go to `.github/workflows/test_model.yml` if the errors are in the testing part. Use `github/workflows/build_upload.yml` for the build & upload the release part.

#### Example:

To __upload artifact to a different container, fix the connection string credentials, or upload a different file__:

Simply go to ```github/workflows/build_upload.yml```, find the ```upload``` job, ```Upload to Azure Blob``` action and replace the corresponding values:

```upload:
    ...
    ...
    - name: Upload to Azure Blob
      uses: bacongobbler/azure-blob-storage-upload@v1.1.1
      with:
        source_dir: model_file
        container_name: challenge
        connection_string: DefaultEndpointsProtocol=https;AccountName=seasaltchallenge;AccountKey=/BllvFebClfScQtmz5kHep8O2PaLAAQKWsRujRnU/sMiMDgv7XHocIfFS31GV7NGHLnsOP4xBrZcUpKmlMP7Gw==;EndpointSuffix=core.windows.net
        sync: false
```

#### Possible extensions:

1. Changes to default flake8 run:
  In ```.github/workflows/test_model.yml```, under ```Lint with flake8``` change:
  ```run:
     flake8 .
  ```
  to 
  ```run:
        # stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
        # call flake8 on a specific file or directory:
        flake8 . <PATH/TO/THE/FILE>
 ```
 More options [here](https://flake8.pycqa.org/en/latest/user/invocation.html#invocation)
       
2. Using multiple Python versions: example job parameters
```
runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [2.7, 3.5, 3.6, 3.7, 3.8]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
```
Check [the documentatoin](https://help.github.com/en/actions/language-and-framework-guides/using-python-with-github-actions) for more options.

See the [Actions Marketplace](https://github.com/marketplace?type=actions) for all available actions,
check the [documentation](https://help.github.com/en/actions) for more information.
