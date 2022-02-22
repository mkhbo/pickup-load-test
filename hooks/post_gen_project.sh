#!/bin/bash
mv {{cookiecutter.airflow}}/ ./..
mv {{cookiecutter.snowflake}}/ ./..
mv {{cookiecutter.sagemaker}}/ ./..
mv {{cookiecutter.python}}/ ./..
mv {{cookiecutter.glue}}/ ./..
{%- if cookiecutter.databricks_profile == 'false' %}
rm {{cookiecutter.databricks}}/ -rf
{% else %}
mv {{cookiecutter.databricks}}/ ./..
{%- endif %}

cd ../
cp -r {{cookiecutter.project_slug}}/* .
cp -r {{cookiecutter.project_slug}}/.* . > /dev/null 2>&1
rm -rf {{cookiecutter.project_slug}}
