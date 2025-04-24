FROM grafana/grafana:latest

RUN ls

COPY ./provisioning/dashboards/*.yml /etc/grafana/provisioning/dashboards/
COPY ./provisioning/datasources/*.yml /etc/grafana/provisioning/datasources/
COPY ./provisioning/dashboards/*.json /var/lib/grafana/dashboards/