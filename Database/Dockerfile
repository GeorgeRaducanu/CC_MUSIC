FROM postgres:13

# Set environment variables for PostgreSQL
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin
ENV POSTGRES_HOST_AUTH_METHOD=trust
ENV POSTGRES_DB=CC_music

# Copy the schema.sql file to the container
COPY schema.sql /docker-entrypoint-initdb.d/