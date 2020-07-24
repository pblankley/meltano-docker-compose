FROM meltano/meltano:latest

WORKDIR /project
COPY . /project

# Install any additional requirements
RUN pip install -r requirements.txt

# Install all plugins into the `.meltano` directory
RUN meltano install

# Pin `discovery.yml` manifest by copying cached version to project root
RUN cp -n .meltano/cache/discovery.yml . 2>/dev/null || :

# Don't allow changes to containerized project
ENV MELTANO_READONLY 1

# Expose default port used by `meltano ui`
EXPOSE 5000

ENTRYPOINT ["meltano"]
