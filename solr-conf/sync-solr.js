/**
 * Implementation of a StatelessScriptUpdateProcessorFactory https://lucene.apache.org/solr/8_4_0/solr-core/org/apache/solr/update/processor/StatelessScriptUpdateProcessorFactory.html.
 * Syncronizes documents to a remote solr configured in remoteCoreURL param.
 * Handles AddUpdateCommand and DeleteUpdateCommand.
 */

/**
 * The remoteCoreURL defines the url to the solr the sync should happen to.
 */
var remoteCoreURL = params.get("remoteCoreURL");
if (!remoteCoreURL) {
  logger.warn(
    "jvm-opts remoteCoreURL is mandatory when using the sync-solr StatelessScriptUpdateProcessor"
  );
}

/**
 * List of portal_types to sync to remote solr
 */
var portalTypesToSyncOption = params.get("portalTypes");
if (!portalTypesToSyncOption) {
  logger.warn(
    "portalTypes is mandatory when using the sync-solr StatelessScriptUpdateProcessor"
  );
}
portalTypesToSync = [];
portalTypesToSyncSplit = portalTypesToSyncOption.split(",");
for (var i = 0; i < portalTypesToSyncSplit.length; i++) {
  portalTypesToSync.push(portalTypesToSyncSplit[i].trim());
}

/**
 * Atomic update modifiers according to https://lucene.apache.org/solr/guide/8_4/updating-parts-of-documents.html
 */
var atomicUpdateModifiers = [
  "set",
  "add",
  "add-distinct",
  "remove",
  "removeregex",
  "inc",
];

/**
 * The commit is written to the file system within this amount of time on the target core
 */
var hardCommitTimeout = 60; // seconds

/**
 * Determines if an object is empty
 * @param {Object} obj
 */
function isObjectEmpty(obj) {
  return JSON.stringify(obj) === "{}";
}

/**
 * Checks if the key is present in the SolrDocument
 * @param {SolrDocument} doc https://lucene.apache.org/solr/8_4_0/solr-solrj/org/apache/solr/common/SolrDocument.html
 * @param {String} key
 * @returns {Boolean} true if the key exists, false otherwise
 */
function keyExists(doc, key) {
  var value = doc.getFieldValue(key);
  return value !== null;
}

/**
 * Casts field value Object to JavaScript String
 * @param {Object} value
 * @returns {String} JavaScript String value
 */
function valueToString(value) {
  return String(value.toString());
}

/**
 * Extracts a value from a document.
 * Returns an objects with three keys.
 * When the isAtomic key is set to true, the document is meant to be an atomic update and the modifier key contains the modifier for the atomic update value.
 * The value key constains the value from the document.
 * @param {SolrDocument} doc https://lucene.apache.org/solr/8_4_0/solr-solrj/org/apache/solr/common/SolrDocument.html
 * @param {String} key
 * @returns {Object}
 */
function extractValueFromDoc(doc, key) {
  var value = valueToString(doc.getFieldValue(key));
  if (value.indexOf("{") === 0 && value.lastIndexOf("}") === value.length - 1) {
    value = value.substring(1, value.length - 1);
    var modifierSplit = value.split("=");
    var modifier = modifierSplit.shift();
    if (atomicUpdateModifiers.indexOf(modifier) > -1) {
      return {
        isAtomic: true,
        modifier: modifier,
        value: modifierSplit.join(""),
      };
    }
  }
  return {
    isAtomic: false,
    modifier: null,
    value: value,
  };
}

function extractValuesFromDoc(doc, key) {
  var values = [];
  var fieldValues = doc.getFieldValues(key);
  for (var iterator = fieldValues.iterator(); iterator.hasNext(); ) {
    var value = iterator.next();
    var stringValue = valueToString(value);
    values.push(stringValue);
  }
  return values;
}

/**
 * Either extracts a single or a multi value from a SolrDocument, depending on the isMultiple flag.
 * When isMultiple is set to true, a multi value is extracted. When isMultiple is set to false, a single value is extracted.
 * @param {SolrDocument} doc https://lucene.apache.org/solr/8_4_0/solr-solrj/org/apache/solr/common/SolrDocument.html
 * @param {String} key
 * @param {Boolean} isMultiple
 */
function extractValue(doc, key, isMultiple) {
  if (!keyExists(doc, key)) {
    return null;
  }
  if (isMultiple === true) {
    return extractValuesFromDoc(doc, key);
  } else {
    return extractValueFromDoc(doc, key);
  }
}

/**
 * Entiches the payload object with the value from the SolrDocument.
 * The key decides which value is extraced.
 * Atomic requests are automatically determined and put on the payload.
 * @param {Object} payload
 * @param {SolrDocument} doc https://lucene.apache.org/solr/8_4_0/solr-solrj/org/apache/solr/common/SolrDocument.html
 * @param {String} key
 * @param {Boolean} isMultiple
 */
function fillPayload(payload, doc, key, isMultiple) {
  extracted = extractValue(doc, key, isMultiple);
  if (extracted !== null) {
    if (extracted.isAtomic) {
      payload[key] = {};
      payload[key][extracted.modifier] = extracted.value;
    } else {
      payload[key] = extracted.value;
    }
  }
  return payload;
}

/**
 * Check if the portal_type of the document is in the list of portal types to sync to the remote solr.
 * If the document has no portal type the sync evaluates true because it may be an atomic update for a document
 * that has already been synced to the remote solr.
 * @param {SolrDocument} doc https://lucene.apache.org/solr/8_4_0/solr-solrj/org/apache/solr/common/SolrDocument.
 */
function checkForSync(doc) {
  if(keyExists(doc, "portal_type")) {
    portalType = extractValueFromDoc(doc, "portal_type");
    if (portalType.isAtomic === false) {
      if (portalTypesToSync.indexOf(portalType.value) === -1) {
        return false;
      }
    }
  }
  return true;
}

/**
 * Reads a java InputSteam
 * @param {InputSteam} inputStream https://docs.oracle.com/javase/7/docs/api/java/io/InputStream.html
 */
function read(inputStream) {
  var inReader = new java.io.BufferedReader(
    new java.io.InputStreamReader(inputStream)
  );
  var inputLine;
  var response = new java.lang.StringBuffer();

  while ((inputLine = inReader.readLine()) != null) {
    response.append(inputLine);
  }
  inReader.close();
  return response.toString();
}

/**
 * Write data to output stream.
 * @param {OutputStream} outputStream https://docs.oracle.com/javase/7/docs/api/java/io/OutputStream.html
 * @param {String} data
 */
function write(outputStream, data) {
  var bw = new java.io.BufferedWriter(new java.io.OutputStreamWriter(outputStream, "UTF-8"))
  bw.write(data);
  bw.flush();
  bw.close();
}

/**
 * Reads data and responseCode from a java URLConnection.
 * @param {URLConnection} con https://docs.oracle.com/javase/7/docs/api/java/net/URLConnection.html
 */
function asResponse(con) {
  var data = read(con.inputStream);
  return { data: data, statusCode: con.responseCode };
}

/**
 * Posts data to an url as json.
 * @param {String} url
 * @param {String} data
 * @param {String} contentType
 */
function httpPost(url, data, contentType) {
  var contentType = contentType || "application/json";
  var con = new java.net.URL(url).openConnection();

  con.requestMethod = "POST";
  con.setRequestProperty("Content-Type", contentType);
  con.setRequestProperty("Accept", "application/json");
  con.doOutput = true;

  write(con.outputStream, data);

  return asResponse(con);
}

/**
 * Submits a SolrDocument to another solr.
 * The target is configured in the remoteCoreURL param in the solrconfig.xml.
 * If the overwrite flag is set, the target solr overwrites the document sent.
 * @param {SolrDocument} doc
 * @param {Boolean} overwrite
 */
function submitDocument(doc, overwrite) {
  var url =
    remoteCoreURL + "/update?commitWithin=" + JSON.stringify(hardCommitTimeout);
  url = url + "&wt=json";
  url = url + "&commit=true";
  if (overwrite) {
    url = url + "&overwrite=" + JSON.stringify(overwrite);
  }
  return httpPost(url, JSON.stringify(doc));
}

/**
 * Handler for AddUpdateCommand.
 * This is called when the solr processes an add command.
 * @param {AddUpdateCommand} cmd https://lucene.apache.org/solr/8_4_0/solr-core/org/apache/solr/update/AddUpdateCommand.html
 */
function processAdd(cmd) {
  try {
    var overwrite = cmd.overwrite;
    var doc = cmd.solrDoc;
    var updateDocument = {};

    // Do not proceed if the document does not need to be synced
    if(!checkForSync(doc)) {
      return;
    }

    // Document id is mandatory
    id = extractValue(doc, "UID").value;

    // List of values sent to remote solr
    updateDocument = fillPayload(updateDocument, doc, "SearchableText");
    updateDocument = fillPayload(updateDocument, doc, "Title");
    updateDocument = fillPayload(updateDocument, doc, "portal_type");
    updateDocument = fillPayload(updateDocument, doc, "trashed");
    updateDocument = fillPayload(updateDocument, doc, "path");
    updateDocument = fillPayload(
      updateDocument,
      doc,
      "allowedRolesAndUsers",
      true
    );
    updateDocument = fillPayload(updateDocument, doc, "bumblebee_checksum");
    // end: list of values

    if (isObjectEmpty(updateDocument)) {
      return;
    }

    updateDocument["UID"] = id;

    var updateDocumentPayload = {
      add: {
        doc: updateDocument,
      },
    };

    var response = submitDocument(updateDocumentPayload, overwrite);
    var statusCode = response.statusCode;
    if (statusCode >= 400) {
      logger.error(
        "An error occured while submitting a document to a remote solr."
      );
      logger.error("Remote Core URL: " + remoteCoreURL);
      logger.error("Status code: " + statusCode);
      logger.error("Response: " + response.data);
      logger.error("Document: " + JSON.stringify(updateDocumentPayload));
    }
  } catch (error) {
    // Proceed to the next chain link when an error occurs
    logger.error(error.message)
    return;
  }
}

/**
 * Handler for DeleteUpdateCommand.
 * This is called when the solr processes a delete command.
 * @param {DeleteUpdateCommand} cmd https://lucene.apache.org/solr/8_4_0/solr-core/org/apache/solr/update/DeleteUpdateCommand.html
 */
function processDelete(cmd) {
  try {
    var id = cmd.id;
    var deleteDocumentPayload = {
      delete: {
        doc: {
          UID: id,
        },
      },
    };

    var response = submitDocument(deleteDocumentPayload);
    var statusCode = response.statusCode;
    if (statusCode >= 400) {
      logger.error(
        "An error occured while deleteing a document to a remote solr."
      );
      logger.error("Remote Core URL: " + remoteCoreURL);
      logger.error("Status code: " + statusCode);
      logger.error("Response: " + response.data);
      logger.error("Document: " + JSON.stringify(deleteDocumentPayload));
    }
  } catch (error) {
    // Proceed to the next chain link when an error occurs
    logger.error(error.message)
    return;
  }
}

// The following functions have to be defined in order for the StatelessScriptUpdateProcessor to work
function processMergeIndexes() {
  /* no-op */
}

function processCommit() {
  /* no-op */
}

function processRollback() {
  /* no-op */
}

function finish() {
  /* no-op */
}
