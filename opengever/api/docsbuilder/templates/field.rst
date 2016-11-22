

   .. py:attribute:: {{ name }}

       {% if title is defined -%}       :Feldname: :field-title:`{{ title }}`    {%- endif %}
       {% if type is defined -%}        :Datentyp: ``{{ type }}``                {%- endif %}
       {% if required is defined -%}    :Pflichtfeld: Ja :required:`(*)`         {%- endif %}
       {% if default is defined -%}     :Default: {{ default }}                  {%- endif %}
       {% if description is defined -%} :Beschreibung: {{ description }}         {%- endif %}
       {% if vocabulary is defined -%}  :Wertebereich: {{ vocabulary }}          {%- endif %}