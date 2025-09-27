import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Transformer } from "markmap-lib";
import { Markmap } from "markmap-view";
import { Worker, Viewer } from "@react-pdf-viewer/core";
import "@react-pdf-viewer/core/lib/styles/index.css";
import { toolbarPlugin } from "@react-pdf-viewer/toolbar";
import "@react-pdf-viewer/toolbar/lib/styles/index.css";
import { thumbnailPlugin } from "@react-pdf-viewer/thumbnail";
import "@react-pdf-viewer/thumbnail/lib/styles/index.css";
import { searchPlugin } from "@react-pdf-viewer/search";
import "@react-pdf-viewer/search/lib/styles/index.css";
import { zoomPlugin } from "@react-pdf-viewer/zoom";
import "@react-pdf-viewer/zoom/lib/styles/index.css";
import { ArrowForward, Download } from "@mui/icons-material";
import html2canvas from "html2canvas";
import CircularProgress from "@mui/material/CircularProgress";
import {
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
} from "@mui/material";

// Available OpenRouter models
const MODELS = [
  { id: "x-ai/grok-4-fast:free", name: "Grok 4 Fast (Free)" },
  { id: "deepseek/deepseek-chat-v3.1:free", name: "DeepSeek Chat v3.1 (Free)" },
  { id: "meta-llama/llama-3.3-70b-instruct:free", name: "LLaMA 3.3 70B Instruct (Free)" },
  { id: "mistralai/mistral-small-3.2-24b-instruct:free", name: "Mistral Small 24B (Free)" },
  { id: "openai/gpt-oss-20b:free", name: "GPT OSS 20B (Free)" },
];

function PDFViewer({ pdfUrl }) {
  const toolbarPluginInstance = toolbarPlugin();
  const { Toolbar } = toolbarPluginInstance;
  const thumbnailPluginInstance = thumbnailPlugin();
  const { Thumbnails } = thumbnailPluginInstance;
  const searchPluginInstance = searchPlugin();
  const zoomPluginInstance = zoomPlugin();

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div
        style={{
          padding: "8px",
          borderBottom: "1px solid rgba(0, 0, 0, 0.12)",
        }}
      >
        <Toolbar />
      </div>
      <div style={{ display: "flex", flex: 1 }}>
        <div
          style={{
            width: "20%",
            borderRight: "1px solid rgba(0, 0, 0, 0.12)",
            padding: "8px",
          }}
        >
          <Thumbnails />
        </div>
        <div style={{ flex: 1 }}>
          <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.4.120/build/pdf.worker.min.js">
            <Viewer
              fileUrl={pdfUrl}
              plugins={[
                toolbarPluginInstance,
                thumbnailPluginInstance,
                searchPluginInstance,
                zoomPluginInstance,
              ]}
            />
          </Worker>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [markdown, setMarkdown] = useState("");
  const [prompt, setPrompt] = useState("");
  const [pdfFile, setPdfFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [model, setModel] = useState(MODELS[0].id);
  const [activeTab, setActiveTab] = useState("pdf"); // pdf, mindmap, summary
  const [modelSummary, setModelSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const svgRef = useRef(null);

  const handleDownloadMindmap = async () => {
    if (!svgRef.current) return;

    try {
      const svgContainer = svgRef.current.parentElement;
      const originalPosition = svgContainer.style.position;
      if (!originalPosition || originalPosition === "static") {
        svgContainer.style.position = "relative";
      }

      const originalBackground = svgContainer.style.background;
      svgContainer.style.background = "white";

      const now = new Date();
      const formattedDate = now.toLocaleDateString("pt-PT");
      const formattedTime = now.toLocaleTimeString("pt-PT");
      const overlayText = `Gerado por: ${model} às ${formattedTime} do dia ${formattedDate}`;

      const infoDiv = document.createElement("div");
      infoDiv.innerText = overlayText;
      infoDiv.style.position = "absolute";
      infoDiv.style.bottom = "10px";
      infoDiv.style.left = "10px";
      infoDiv.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
      infoDiv.style.padding = "5px";
      infoDiv.style.fontSize = "12px";
      infoDiv.style.zIndex = "1000";

      svgContainer.appendChild(infoDiv);

      const canvas = await html2canvas(svgContainer, {
        backgroundColor: "#ffffff",
        scale: 2,
        logging: false,
        width: svgContainer.scrollWidth,
        height: svgContainer.scrollHeight,
        allowTaint: false,
        useCORS: true,
      });

      svgContainer.removeChild(infoDiv);
      svgContainer.style.background = originalBackground;
      svgContainer.style.position = originalPosition;

      canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.download = "mindmap.png";
        link.href = url;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }, "image/png");
    } catch (error) {
      console.error("Error during download:", error);
      alert("Houve um erro ao gerar a imagem. Por favor, tente novamente.");
    }
  };

  useEffect(() => {
    if (pdfFile) {
      const fileUrl = URL.createObjectURL(pdfFile);
      setPdfUrl(fileUrl);
      return () => URL.revokeObjectURL(fileUrl);
    }
  }, [pdfFile]);

  useEffect(() => {
    if (markdown && svgRef.current && activeTab === "mindmap") {
      svgRef.current.innerHTML = "";
      try {
        const transformer = new Transformer();
        const { root } = transformer.transform(markdown);
        const mm = Markmap.create(svgRef.current, {}, root);
        mm.fit();
      } catch (error) {
        console.error("Error creating Markmap:", error);
      }
    }
  }, [markdown, activeTab]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMarkdown("");
    setLoading(true);

    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("model", model);
    if (pdfFile) formData.append("pdf_file", pdfFile);
    if (audioFile) formData.append("audio_file", audioFile);

    try {
      const response = await axios.post("http://localhost:8000/process-file", formData);
      setMarkdown(response.data.markdown);
      setModelSummary(response.data.model_summary || "");
    } catch (error) {
      console.error("Error generating mind map:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflow: "auto",
        position: "relative",
      }}
    >
      <div style={{ display: "flex", flex: 1, overflow: "auto" }}>
        {/* Left Panel */}
        <div
          style={{
            width: "300px",
            borderRight: "1px solid rgba(0, 0, 0, 0.12)",
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
          }}
        >
          <FormControl fullWidth>
            <InputLabel>Modelo</InputLabel>
            <Select value={model} onChange={(e) => setModel(e.target.value)} label="Modelo">
              {MODELS.map((m) => (
                <MenuItem key={m.id} value={m.id}>
                  {m.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button variant="contained" component="label" fullWidth>
            Submeter PDF
            <input
              type="file"
              accept=".pdf"
              hidden
              onChange={(e) => setPdfFile(e.target.files[0])}
            />
          </Button>
          {pdfFile && (
            <div style={{ marginTop: "5px", fontSize: "0.8rem" }}>{pdfFile.name}</div>
          )}

          <Button variant="contained" component="label" fullWidth>
            Submeter Áudio
            <input
              type="file"
              accept="audio/*"
              hidden
              onChange={(e) => setAudioFile(e.target.files[0])}
            />
          </Button>
          {audioFile && (
            <div style={{ marginTop: "5px", fontSize: "0.8rem" }}>{audioFile.name}</div>
          )}
        </div>

        {/* Right Panel */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {/* Tabs */}
          <div
            style={{
              display: "flex",
              borderBottom: "1px solid rgba(0, 0, 0, 0.12)",
              backgroundColor: "#f5f5f5",
            }}
          >
            <Button
              onClick={() => setActiveTab("pdf")}
              style={{
                flex: 1,
                padding: "15px",
                borderRadius: 0,
                backgroundColor: activeTab === "pdf" ? "#ffffff" : "transparent",
              }}
            >
              PDF Viewer
            </Button>
            <Button
              onClick={() => setActiveTab("mindmap")}
              style={{
                flex: 1,
                padding: "15px",
                borderRadius: 0,
                backgroundColor: activeTab === "mindmap" ? "#ffffff" : "transparent",
              }}
            >
              Mapa Mental
            </Button>
            <Button
              onClick={() => setActiveTab("summary")}
              style={{
                flex: 1,
                padding: "15px",
                borderRadius: 0,
                backgroundColor: activeTab === "summary" ? "#ffffff" : "transparent",
              }}
            >
              Resumo do modelo
            </Button>
            {activeTab === "mindmap" && markdown && (
              <Tooltip title="Download Mind Map">
                <IconButton
                  onClick={handleDownloadMindmap}
                  style={{
                    margin: "8px",
                    backgroundColor: "#f0f0f0",
                  }}
                >
                  <Download />
                </IconButton>
              </Tooltip>
            )}
          </div>

          {/* Content Area */}
          <div style={{ flex: 1, overflow: "auto" }}>
            {activeTab === "pdf" && pdfUrl && (
              <div style={{ height: "100%" }}>
                <PDFViewer pdfUrl={pdfUrl} />
              </div>
            )}

            {activeTab === "mindmap" && (
              <div style={{ width: "100%", height: "100%", position: "relative" }}>
                {loading ? (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      height: "100%",
                    }}
                  >
                    <CircularProgress />
                  </div>
                ) : (
                  <svg ref={svgRef} style={{ width: "100%", height: "100%" }}></svg>
                )}
              </div>
            )}

            {activeTab === "summary" && (
              <div
                style={{
                  padding: "20px",
                  overflow: "auto",
                  height: "100%",
                  whiteSpace: "pre-wrap",
                }}
              >
                {modelSummary}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Prompt Area */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: "300px", // Width of left panel
          right: 0,
          padding: "20px",
          backgroundColor: "#ffffff",
          borderTop: "1px solid rgba(0, 0, 0, 0.12)",
          display: "flex",
          gap: "10px",
        }}
      >
        <TextField
          placeholder="Ex: Gera um mapa mental sobre o conteúdo do PDF"
          variant="outlined"
          multiline
          rows={2}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          style={{ flex: 1 }}
        />
        <IconButton color="primary" onClick={handleSubmit}>
          <ArrowForward />
        </IconButton>
      </div>
    </div>
  );
}

export default App;
