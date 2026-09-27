import React, { useEffect, useState } from "react";
import { api, downloadAuthedFile } from "../services/api.js";

export default function Files() {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const load = () =>
    api
      .listFiles()
      .then(setFiles)
      .catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setError("");
    setUploading(true);
    try {
      await api.uploadFile(file);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (fileId) => {
    try {
      await api.deleteFile(fileId);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">Your keepsakes</p>
        <h1>Files, all in one place.</h1>
        <p className="subtitle">A handy place for meal notes, exports, and other things you want to keep with your plans.</p>
      </div>
      <div className="card content-card">

      <label htmlFor="file-upload">Add a file <span className="muted">· image, PDF, or text up to 5MB</span></label>
      <input id="file-upload" type="file" onChange={handleUpload} disabled={uploading} />
      {uploading && <p className="muted">Adding your file…</p>}
      {error && <p className="error-text">{error}</p>}

      {files.length === 0 && <div className="empty-state">Nothing saved here yet. Add a file and it’ll be easy to find later.</div>}

      {files.map((f) => (
        <div className="list-row" key={f.file_id}>
          <div>
            <strong>{f.filename}</strong>
            <div className="subtitle file-meta">
              {(f.size_bytes / 1024).toFixed(1)} KB &middot;{" "}
              {new Date(f.uploaded_at).toLocaleString()}
            </div>
          </div>
          <div className="row-actions">
            <button className="secondary small"
              onClick={() =>
                downloadAuthedFile(api.downloadUrl(f.file_id), f.filename)
              }
            >
              Download
            </button>
            <button className="danger small" onClick={() => handleDelete(f.file_id)}>
              Delete
            </button>
          </div>
        </div>
      ))}
      </div>
    </>
  );
}
