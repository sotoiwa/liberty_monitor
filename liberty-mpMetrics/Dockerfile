FROM websphere-liberty:18.0.0.4-webProfile8
COPY --chown=1001:0 server.xml /config/
COPY --chown=1001:0 sample.war /config/apps/
RUN installUtility install --acceptLicense defaultServer