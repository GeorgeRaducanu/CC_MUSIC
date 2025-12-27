{{/*
============================================================================
CC_MUSIC - Helper Templates
============================================================================
Acest fișier conține funcții helper reutilizabile în toate template-urile.
*/}}

{{/*
Generează numele complet al chart-ului
*/}}
{{- define "cc-music.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Generează numele chart-ului
*/}}
{{- define "cc-music.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Generează etichete comune pentru toate resursele
*/}}
{{- define "cc-music.labels" -}}
helm.sh/chart: {{ include "cc-music.chart" . }}
{{ include "cc-music.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Generează etichete selector
*/}}
{{- define "cc-music.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cc-music.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Generează numele chart-ului și versiunea pentru etichetare
*/}}
{{- define "cc-music.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Generează numele serviciului pentru un microserviciu specific
*/}}
{{- define "cc-music.serviceName" -}}
{{- printf "%s-%s" .Release.Name .name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Generează namespace-ul
*/}}
{{- define "cc-music.namespace" -}}
{{- default .Release.Namespace .Values.global.namespace }}
{{- end }}
