# oracle_pcrf_kpi
Oracle PCRF KPIs stats converter

## Prerequisites 
List of the packages in venv environment:

Package         Version
--------------- -----------
contourpy       1.3.3

cycler          0.12.1

defusedxml      0.7.1

fonttools       4.62.1

kiwisolver      1.5.0

matplotlib      3.10.8

numpy           2.4.4

odfpy           1.4.1

packaging       26.1

pillow          12.2.0

pip             24.2

pyparsing       3.3.2

python-dateutil 2.9.0.post0

six             1.17.0

## Usage

### 1 - convert xml to csv

Run 'python3 xml_to_csv' converter

Find csv output files in the csv folder 

### 2 - check report template

Check template in 'pcrf_graph_suggester_output.md'. Define metrics to be visualised.

### 3 - run report builder

Run 'build_report.sh'

It will do the following:

1) by launching 'visualize_panels.py' it will create a lot of png files in charts folder. Each graph will be created according to the template defined. Along with png files, it will create 'index.md' document referring to all chart files.

2) by launching 'md_to_odt.py' it will create ODT document with embedded images from 'index.md'

### 4 - check the report

Check 'charts_report_xxx.odt' document as result
