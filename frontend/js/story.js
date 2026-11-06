/**
 * StoryVerse AI — Story Generator Frontend Controller (story.js)
 * Full integration for Phase 5:
 *   - Form parameter handling & live summary sidebar
 *   - POST /api/generate-story
 *   - Operations: POST /api/regenerate, /api/expand, /api/shorten, /api/continue
 *   - Structured Outline vs. Editable Manuscript view modes
 *   - Safe text rendering (no unescaped innerHTML with untrusted AI text)
 *   - Clipboard copy utility
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    // Form & Input elements
    const form = document.getElementById('storyForm');
    if (!form) return;

    const topicInput = document.getElementById('topic');
    const genreSelect = document.getElementById('genre');
    const languageSelect = document.getElementById('language');
    const toneSelect = document.getElementById('tone');
    const lengthSelect = document.getElementById('length');
    const audienceSelect = document.getElementById('audience');
    const charCountInput = document.getElementById('characterCount');
    const charNamesInput = document.getElementById('characterNames');
    const settingInput = document.getElementById('setting');
    const instructionsInput = document.getElementById('instructions');
    const generateBtn = document.getElementById('generateStoryBtn');
    const topicCharCount = document.getElementById('topicCharCount');
    const useRagCheckbox = document.getElementById('storyUseRag');

    // Sidebar Summary elements
    const summaryGenre = document.getElementById('summaryGenre');
    const summaryLanguage = document.getElementById('summaryLanguage');
    const summaryTone = document.getElementById('summaryTone');
    const summaryLength = document.getElementById('summaryLength');

    // Result & Loading elements
    const loadingState = document.getElementById('storyLoadingState');
    const loadingTitle = document.getElementById('loadingTitle');
    const loadingDesc = document.getElementById('loadingDesc');
    const resultSection = document.getElementById('storyResultSection');
    const resultTitle = document.getElementById('resultStoryTitle');
    const resultGenreBadge = document.getElementById('resultGenreBadge');
    const resultLanguageBadge = document.getElementById('resultLanguageBadge');
    const resultToneBadge = document.getElementById('resultToneBadge');
    const resultLengthBadge = document.getElementById('resultLengthBadge');

    // Action Buttons
    const copyBtn = document.getElementById('storyCopyBtn');
    const regenerateBtn = document.getElementById('storyRegenerateBtn');
    const expandBtn = document.getElementById('storyExpandBtn');
    const shortenBtn = document.getElementById('storyShortenBtn');
    const continueBtn = document.getElementById('storyContinueBtn');

    // View Mode elements
    const viewStructuredBtn = document.getElementById('viewStructuredBtn');
    const viewEditableBtn = document.getElementById('viewEditableBtn');
    const structuredView = document.getElementById('structuredView');
    const editableView = document.getElementById('editableView');
    const editableTextarea = document.getElementById('storyEditableTextarea');
    const editableCharCounter = document.getElementById('editableCharCounter');

    // Section Content holders
    const sectionSummary = document.getElementById('sectionSummary');
    const sectionSetting = document.getElementById('sectionSetting');
    const sectionCharacters = document.getElementById('sectionCharacters');
    const sectionIntro = document.getElementById('sectionIntro');
    const sectionMainPlot = document.getElementById('sectionMainPlot');
    const sectionClimax = document.getElementById('sectionClimax');
    const sectionConclusion = document.getElementById('sectionConclusion');
    const sectionMoral = document.getElementById('sectionMoral');

    // Current generation state
    let activeStoryData = null;

    // --- Live Parameter Preview & Character Counter ---
    if (topicInput && topicCharCount) {
      topicInput.addEventListener('input', () => {
        topicCharCount.textContent = `${topicInput.value.length} / 2000`;
      });
    }

    function updateSummary() {
      if (summaryGenre && genreSelect) summaryGenre.textContent = genreSelect.value;
      if (summaryLanguage && languageSelect) summaryLanguage.textContent = languageSelect.value;
      if (summaryTone && toneSelect) summaryTone.textContent = toneSelect.value;
      if (summaryLength && lengthSelect) summaryLength.textContent = lengthSelect.value;
    }

    [genreSelect, languageSelect, toneSelect, lengthSelect].forEach(el => {
      if (el) el.addEventListener('change', updateSummary);
    });

    if (editableTextarea && editableCharCounter) {
      editableTextarea.addEventListener('input', () => {
        editableCharCounter.textContent = `${editableTextarea.value.length.toLocaleString()} characters`;
      });
    }

    // --- View Mode Toggle ---
    if (viewStructuredBtn && viewEditableBtn) {
      viewStructuredBtn.addEventListener('click', () => {
        viewStructuredBtn.classList.add('active');
        viewEditableBtn.classList.remove('active');
        structuredView.style.display = 'flex';
        editableView.style.display = 'none';
      });

      viewEditableBtn.addEventListener('click', () => {
        viewEditableBtn.classList.add('active');
        viewStructuredBtn.classList.remove('active');
        structuredView.style.display = 'none';
        editableView.style.display = 'block';
      });
    }

    // --- Loading State Helper ---
    function setLoading(isLoading, title = "StoryVerse AI is weaving your story...", desc = "Crafting characters, conflicts, and climatic arcs") {
      if (isLoading) {
        if (loadingTitle) loadingTitle.textContent = title;
        if (loadingDesc) loadingDesc.textContent = desc;
        if (loadingState) loadingState.style.display = 'block';
        if (resultSection) resultSection.style.display = 'none';
        if (generateBtn) {
          generateBtn.disabled = true;
          generateBtn.innerHTML = '<span class="spinner"></span> <span>Generating...</span>';
        }
        loadingState.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        if (loadingState) loadingState.style.display = 'none';
        if (generateBtn) {
          generateBtn.disabled = false;
          generateBtn.innerHTML = '<span>✨ Generate Full Story</span>';
        }
      }
    }

    // --- Safe Text Display Rendering ---
    function renderStoryResult(storyData) {
      activeStoryData = storyData;

      // Safe textContent assignment (never unsafe innerHTML)
      if (resultTitle) resultTitle.textContent = storyData.title || "Untitled Story";
      if (resultGenreBadge) resultGenreBadge.textContent = storyData.metadata?.genre || genreSelect.value;
      if (resultLanguageBadge) resultLanguageBadge.textContent = storyData.metadata?.language || languageSelect.value;
      if (resultToneBadge) resultToneBadge.textContent = storyData.metadata?.tone || toneSelect.value;
      if (resultLengthBadge) resultLengthBadge.textContent = storyData.metadata?.length || lengthSelect.value;

      // Sections
      if (sectionSummary) sectionSummary.textContent = storyData.summary || "(Not specified in outline)";
      if (sectionSetting) sectionSetting.textContent = storyData.setting || "(Not specified in outline)";
      if (sectionCharacters) sectionCharacters.textContent = storyData.characters || "(Not specified in outline)";
      if (sectionIntro) sectionIntro.textContent = storyData.introduction || "(Not specified in outline)";
      if (sectionMainPlot) sectionMainPlot.textContent = storyData.main_plot || storyData.full_text;
      if (sectionClimax) sectionClimax.textContent = storyData.climax || "(Not specified in outline)";
      if (sectionConclusion) sectionConclusion.textContent = storyData.conclusion || "(Not specified in outline)";
      if (sectionMoral) sectionMoral.textContent = storyData.moral || "(Not specified in outline)";

      // Full Editable Manuscript
      if (editableTextarea) {
        editableTextarea.value = storyData.full_text || "";
        if (editableCharCounter) {
          editableCharCounter.textContent = `${editableTextarea.value.length.toLocaleString()} characters`;
        }
      }

      // RAG Knowledge Context Banner
      const ragBanner = document.getElementById('storyRagContextBanner');
      const ragChunkCount = document.getElementById('storyRagChunkCount');
      const ragChipsContainer = document.getElementById('storyRagChipsContainer');

      if (ragBanner && ragChipsContainer) {
        ragChipsContainer.innerHTML = '';
        const retrieved = storyData.retrieved_context || [];
        if (retrieved && retrieved.length > 0) {
          if (ragChunkCount) ragChunkCount.textContent = retrieved.length;
          retrieved.forEach(chunk => {
            const chip = document.createElement('div');
            chip.className = 'rag-chunk-chip';
            chip.style.cssText = 'background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 6px; padding: 6px 10px; font-size: 0.8rem; color: #bfdbfe; max-width: 100%;';

            const titleEl = document.createElement('strong');
            titleEl.textContent = `[${chunk.document_title || 'Lore'}] `;
            titleEl.style.color = '#93c5fd';
            chip.appendChild(titleEl);

            const textEl = document.createElement('span');
            const snippet = (chunk.text || '').slice(0, 120);
            textEl.textContent = snippet + (chunk.text && chunk.text.length > 120 ? '...' : '');
            chip.appendChild(textEl);

            ragChipsContainer.appendChild(chip);
          });
          ragBanner.style.display = 'block';
        } else {
          ragBanner.style.display = 'none';
        }
      }

      if (resultSection) {
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    // --- Form Submission: POST /api/generate-story ---
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const topic = topicInput ? topicInput.value.trim() : "";
      if (!topic) {
        if (window.StoryVerse) window.StoryVerse.showToast("Please enter a story topic or core premise.", "warning");
        if (topicInput) topicInput.focus();
        return;
      }

      // Collect parameters
      let characterNames = [];
      if (charNamesInput && charNamesInput.value.trim()) {
        characterNames = charNamesInput.value.split(',').map(n => n.trim()).filter(Boolean);
      }

      const payload = {
        topic: topic,
        genre: genreSelect ? genreSelect.value : "Fantasy",
        language: languageSelect ? languageSelect.value : "English",
        tone: toneSelect ? toneSelect.value : "Emotional",
        length: lengthSelect ? lengthSelect.value : "Medium",
        audience: audienceSelect ? audienceSelect.value : "General Audience",
        character_count: charCountInput ? parseInt(charCountInput.value, 10) : 2,
        character_names: characterNames,
        setting: settingInput ? settingInput.value.trim() : "",
        additional_instructions: instructionsInput ? instructionsInput.value.trim() : "",
        use_rag: useRagCheckbox ? useRagCheckbox.checked : true
      };

      setLoading(true, "StoryVerse AI is generating your story...", `Writing in ${payload.language} (${payload.genre})`);

      try {
        const response = await window.StoryVerseAPI.generateStory(payload);
        if (response && response.success && response.data) {
          renderStoryResult(response.data);
          if (window.StoryVerse) {
            window.StoryVerse.showToast("Story generated successfully!", "success");
          }
        } else {
          throw new Error(response.message || "Failed to generate story.");
        }
      } catch (err) {
        console.error("Story Generation Error:", err);
        const errMsg = err.message || "An unexpected error occurred during generation.";
        if (window.StoryVerse) {
          window.StoryVerse.showToast(errMsg, "error", 6000);
        }
      } finally {
        setLoading(false);
      }
    });

    // --- Operation 1: Regenerate ---
    if (regenerateBtn) {
      regenerateBtn.addEventListener('click', async () => {
        const currentContent = editableTextarea ? editableTextarea.value.trim() : "";
        setLoading(true, "Regenerating story draft...", "Infusing fresh perspectives and elevated tension");

        try {
          const payload = {
            content: currentContent,
            topic: topicInput ? topicInput.value.trim() : undefined,
            genre: genreSelect ? genreSelect.value : undefined,
            language: languageSelect ? languageSelect.value : undefined,
            instructions: instructionsInput ? instructionsInput.value.trim() : undefined
          };
          const response = await window.StoryVerseAPI.regenerateStory(payload);
          if (response && response.success && response.data) {
            renderStoryResult(response.data);
            if (window.StoryVerse) window.StoryVerse.showToast("Story regenerated!", "success");
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || "Regeneration failed.", "error");
        } finally {
          setLoading(false);
        }
      });
    }

    // --- Operation 2: Expand ---
    if (expandBtn) {
      expandBtn.addEventListener('click', async () => {
        const currentContent = editableTextarea ? editableTextarea.value.trim() : "";
        if (!currentContent) {
          if (window.StoryVerse) window.StoryVerse.showToast("No story content to expand.", "warning");
          return;
        }

        setLoading(true, "Expanding story with sensory details...", "Enriching world textures and character depths");

        try {
          const payload = {
            content: currentContent,
            language: languageSelect ? languageSelect.value : "English"
          };
          const response = await window.StoryVerseAPI.expandStory(payload);
          if (response && response.success && response.data) {
            editableTextarea.value = response.data.full_text;
            if (editableCharCounter) {
              editableCharCounter.textContent = `${editableTextarea.value.length.toLocaleString()} characters`;
            }
            // Switch to editable view to see full expansion
            if (viewEditableBtn) viewEditableBtn.click();
            if (window.StoryVerse) window.StoryVerse.showToast("Story expanded with sensory details!", "success");
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || "Expansion failed.", "error");
        } finally {
          setLoading(false);
        }
      });
    }

    // --- Operation 3: Shorten ---
    if (shortenBtn) {
      shortenBtn.addEventListener('click', async () => {
        const currentContent = editableTextarea ? editableTextarea.value.trim() : "";
        if (!currentContent) {
          if (window.StoryVerse) window.StoryVerse.showToast("No story content to shorten.", "warning");
          return;
        }

        setLoading(true, "Condensing narrative beats...", "Sharpening pace and trimming excess details");

        try {
          const payload = {
            content: currentContent,
            target_reduction: "50%"
          };
          const response = await window.StoryVerseAPI.shortenStory(payload);
          if (response && response.success && response.data) {
            editableTextarea.value = response.data.full_text;
            if (editableCharCounter) {
              editableCharCounter.textContent = `${editableTextarea.value.length.toLocaleString()} characters`;
            }
            if (viewEditableBtn) viewEditableBtn.click();
            if (window.StoryVerse) window.StoryVerse.showToast("Story tightened and condensed!", "success");
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || "Shorten failed.", "error");
        } finally {
          setLoading(false);
        }
      });
    }

    // --- Operation 4: Continue ---
    if (continueBtn) {
      continueBtn.addEventListener('click', async () => {
        const currentContent = editableTextarea ? editableTextarea.value.trim() : "";
        if (!currentContent) {
          if (window.StoryVerse) window.StoryVerse.showToast("No story content to continue.", "warning");
          return;
        }

        setLoading(true, "Continuing the narrative arc...", "Developing the next dramatic complication");

        try {
          const payload = {
            content: currentContent,
            language: languageSelect ? languageSelect.value : "English"
          };
          const response = await window.StoryVerseAPI.continueStory(payload);
          if (response && response.success && response.data) {
            editableTextarea.value = response.data.full_text;
            if (editableCharCounter) {
              editableCharCounter.textContent = `${editableTextarea.value.length.toLocaleString()} characters`;
            }
            if (viewEditableBtn) viewEditableBtn.click();
            if (window.StoryVerse) window.StoryVerse.showToast("Story continued successfully!", "success");
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || "Continuation failed.", "error");
        } finally {
          setLoading(false);
        }
      });
    }

    // --- Operation 5: Copy to Clipboard ---
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        const textToCopy = editableTextarea ? editableTextarea.value : "";
        if (!textToCopy) {
          if (window.StoryVerse) window.StoryVerse.showToast("No story text available to copy.", "warning");
          return;
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(textToCopy).then(() => {
            if (window.StoryVerse) window.StoryVerse.showToast("Full story copied to clipboard!", "success");
          }).catch(() => {
            fallbackCopy(textToCopy);
          });
        } else {
          fallbackCopy(textToCopy);
        }
      });
    }

    // --- Operation 6: Save as Project ---
    const saveProjectBtn = document.getElementById('storySaveProjectBtn');
    if (saveProjectBtn) {
      saveProjectBtn.addEventListener('click', async () => {
        const titleEl = document.getElementById('resultStoryTitle');
        const title = titleEl ? titleEl.textContent.trim() : "Generated Story";
        const content = editableTextarea ? editableTextarea.value.trim() : "";
        if (!content) {
          if (window.StoryVerse) window.StoryVerse.showToast("No story content to save.", "warning");
          return;
        }

        saveProjectBtn.disabled = true;
        try {
          const res = await window.StoryVerseAPI.createProject({
            title: title,
            content_type: 'story',
            genre: genreSelect ? genreSelect.value : undefined,
            language: languageSelect ? languageSelect.value : "English",
            tone: toneSelect ? toneSelect.value : undefined,
            topic: topicInput ? topicInput.value.trim() : undefined,
            content: content
          });

          if (res.success && res.data) {
            if (window.StoryVerse) {
              window.StoryVerse.showToast(`Story saved to portfolio! Project #${res.data.id}`, "success");
            }
          } else {
            throw new Error(res.message || "Failed to save project.");
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || "Error saving project.", "error");
        } finally {
          saveProjectBtn.disabled = false;
        }
      });
    }

    // Export dropdown toggle + per-format download
    const storyExportBtn = document.getElementById('storyExportBtn');
    const storyExportMenu = document.getElementById('storyExportMenu');
    if (storyExportBtn && storyExportMenu) {
      storyExportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        storyExportMenu.style.display = storyExportMenu.style.display === 'none' ? 'flex' : 'none';
      });
      document.addEventListener('click', () => { storyExportMenu.style.display = 'none'; });

      storyExportMenu.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', async () => {
          const format = item.dataset.format;
          storyExportMenu.style.display = 'none';
          const title = document.getElementById('resultStoryTitle')?.textContent.trim() || 'Generated Story';
          const content = editableTextarea ? editableTextarea.value.trim() : '';
          if (!content) {
            if (window.StoryVerse) window.StoryVerse.showToast('No story content to export.', 'warning');
            return;
          }
          item.disabled = true;
          try {
            if (window.StoryVerse) window.StoryVerse.showToast(`Preparing ${format.toUpperCase()} download...`, 'info');
            await window.StoryVerseAPI.exportDocument(format, {
              title: title,
              content: content,
              project_type: 'story',
              genre: genreSelect ? genreSelect.value : undefined,
              language: languageSelect ? languageSelect.value : 'English'
            });
            if (window.StoryVerse) window.StoryVerse.showToast(`${format.toUpperCase()} downloaded successfully!`, 'success');
          } catch (err) {
            if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Export failed.', 'error');
          } finally {
            item.disabled = false;
          }
        });
      });
    }

    function fallbackCopy(text) {
      const tempTextArea = document.createElement('textarea');
      tempTextArea.value = text;
      document.body.appendChild(tempTextArea);
      tempTextArea.select();
      document.execCommand('copy');
      document.body.removeChild(tempTextArea);
      if (window.StoryVerse) window.StoryVerse.showToast("Full story copied to clipboard!", "success");
    }
  });
})();
