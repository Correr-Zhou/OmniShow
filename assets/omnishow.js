(() => {
  const TASKS_BASE = "./assets/tasks/";
  const TASK_SECTION_IDS = ["r2v", "ra2v", "rp2v", "rap2v"];
  const DEFAULT_CASES_COLLAPSE_LIMIT = 4;
  const CASES_COLLAPSE_LIMITS = {
    r2v: 3,
    ra2v: 3,
    rp2v: 3
  };

  const getCasesCollapseLimit = (sectionId) => {
    const n = CASES_COLLAPSE_LIMITS[sectionId];
    return Number.isFinite(n) ? n : DEFAULT_CASES_COLLAPSE_LIMIT;
  };

  const fetchText = async (url) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to load: ${url}`);
    return res.text();
  };

  const fetchJson = async (url) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to load: ${url}`);
    return res.json();
  };

  const resolveUrl = (base, rel) => {
    try {
      return new URL(rel, new URL(base, window.location.href)).toString();
    } catch (_) {
      return rel;
    }
  };

  const setDeferredVideoSource = (video, src, type) => {
    if (!video || !src) return;
    video.dataset.src = src;
    video.dataset.srcType = type || "video/mp4";
    if (video.dataset.srcLoaded !== "true") video.dataset.srcLoaded = "false";
  };

  const prepareDeferredVideoElement = (video) => {
    if (!video || video.dataset.deferredPrepared === "true") return;
    if (video.dataset) video.dataset.deferredPrepared = "true";

    const source = video.querySelector("source[src]");
    const sourceSrc = source && source.getAttribute("src");
    const sourceType = source && source.getAttribute("type");
    if (!sourceSrc) return;

    setDeferredVideoSource(video, sourceSrc, sourceType || "video/mp4");

    if (video.currentSrc || video.readyState > 0) {
      video.dataset.srcLoaded = "true";
      return;
    }

    source.removeAttribute("src");
    try {
      video.load();
    } catch (_) {}
  };

  const ensureVideoSourceLoaded = (video) => {
    if (!video) return;
    if (video.dataset && video.dataset.deferredPrepared !== "true") {
      prepareDeferredVideoElement(video);
    }
    if (video.dataset && video.dataset.srcLoaded === "true") return;

    const src = video.dataset ? video.dataset.src || "" : "";
    if (!src) return;

    let source = video.querySelector("source");
    if (!source) {
      source = document.createElement("source");
      video.appendChild(source);
    }
    source.src = src;
    source.type = (video.dataset && video.dataset.srcType) || "video/mp4";

    try {
      video.load();
    } catch (_) {}
    if (video.dataset) video.dataset.srcLoaded = "true";
  };

  const playVideoSafely = (video) => {
    if (!video) return;
    ensureVideoSourceLoaded(video);
    try {
      const p = video.play();
      if (p && typeof p.catch === "function") p.catch(() => {});
    } catch (_) {}
  };

  const pauseVideoSafely = (video) => {
    if (!video) return;
    try {
      video.pause();
    } catch (_) {}
  };

  const formatCaseLabel = (caseName) => {
    const raw = String(caseName || "");
    const m = raw.match(/case-(\d+)/i);
    if (!m) return raw || "Case";
    const n = String(m[1] || "");
    const digits = n.length >= 2 ? n : n.padStart(2, "0");
    return `Case ${digits}`;
  };

  const normalizeIndex = (raw) => {
    if (!raw || typeof raw !== "object") return null;
    if (raw.sections && typeof raw.sections === "object") return raw.sections;
    const out = {};
    TASK_SECTION_IDS.forEach((id) => {
      if (Array.isArray(raw[id])) out[id] = raw[id];
    });
    if (Object.keys(out).length) return out;
    return null;
  };

  const discoverCasesFromDirListing = async (sectionId) => {
    const listingUrl = `${TASKS_BASE}${sectionId}/`;
    const html = await fetchText(listingUrl);
    const re = /href="(case-[^"\/]+\/)"/g;
    const cases = [];
    let m = null;
    while ((m = re.exec(html))) {
      const name = (m[1] || "").replace(/\/$/, "");
      if (!cases.includes(name)) cases.push(name);
    }
    return cases.sort();
  };

  const loadTasksIndex = async () => {
    try {
      const raw = await fetchJson(`${TASKS_BASE}index.json`);
      const sections = normalizeIndex(raw);
      if (sections) return sections;
    } catch (_) {}

    const sections = {};
    for (let i = 0; i < TASK_SECTION_IDS.length; i += 1) {
      const id = TASK_SECTION_IDS[i];
      try {
        sections[id] = await discoverCasesFromDirListing(id);
      } catch (_) {
        sections[id] = [];
      }
    }
    return sections;
  };

  const createTextCard = (text) => {
    const card = document.createElement("div");
    card.className = "input-card";
    const label = document.createElement("div");
    label.className = "input-label";
    label.textContent = "Text";
    const box = document.createElement("div");
    box.className = "input-text input-text-scroll";
    box.dataset.autoscroll = "true";
    const inner = document.createElement("div");
    inner.className = "input-text-inner";
    inner.textContent = (text || "").trim();
    box.appendChild(inner);
    card.appendChild(label);
    card.appendChild(box);
    return card;
  };

  const createRefCard = (refs, caseBase) => {
    const card = document.createElement("div");
    card.className = "input-card input-card-ref";
    const label = document.createElement("div");
    label.className = "input-label";
    label.textContent = "Reference Images";
    const grid = document.createElement("div");
    grid.className = "ref-grid";
    (refs || []).forEach((src, idx) => {
      const img = document.createElement("img");
      img.className = "ref-img";
      img.src = resolveUrl(caseBase, src);
      img.alt = `Reference image ${idx + 1}`;
      grid.appendChild(img);
    });
    card.appendChild(label);
    card.appendChild(grid);
    return card;
  };

  const createAudioCard = (audioSrc, caseBase) => {
    const card = document.createElement("div");
    card.className = "input-card";
    const label = document.createElement("div");
    label.className = "input-label";
    label.textContent = "Audio";
    const audio = document.createElement("audio");
    audio.className = "audio-player";
    audio.controls = true;
    audio.setAttribute("controlslist", "nodownload noplaybackrate noremoteplayback");
    audio.preload = "metadata";
    const source = document.createElement("source");
    source.src = resolveUrl(caseBase, audioSrc);
    const ext = (audioSrc || "").toLowerCase().split(".").pop();
    source.type = ext === "mp3" ? "audio/mpeg" : "audio/wav";
    audio.appendChild(source);
    card.appendChild(label);
    card.appendChild(audio);
    return card;
  };

  const createPoseCard = (poseSrc, caseBase) => {
    const card = document.createElement("div");
    card.className = "input-card input-card-pose";
    const label = document.createElement("div");
    label.className = "input-label";
    label.textContent = "Pose";
    const wrap = document.createElement("div");
    wrap.className = "portrait-video portrait-video-input";
    const video = document.createElement("video");
    video.className = "lazy-video";
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = "none";
    setDeferredVideoSource(video, resolveUrl(caseBase, poseSrc), "video/mp4");
    wrap.appendChild(video);
    card.appendChild(label);
    card.appendChild(wrap);
    return card;
  };

  const createVideoCard = (output, caseBase, caseName) => {
    const card = document.createElement("div");
    card.className = "video-card";
    const label = document.createElement("div");
    label.className = "video-label";
    label.textContent = output.label || "";
    if ((output.kind || "").toLowerCase() === "ours") label.classList.add("video-label-ours");
    const wrap = document.createElement("div");
    wrap.className = "portrait-video portrait-video-xl";
    const badge = document.createElement("div");
    badge.className = "case-badge";
    badge.textContent = (output && output.label) || formatCaseLabel(caseName);
    badge.setAttribute("aria-hidden", "true");
    const video = document.createElement("video");
    video.className = "lazy-video";
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = "none";
    setDeferredVideoSource(video, resolveUrl(caseBase, output.src || ""), "video/mp4");
    wrap.appendChild(badge);
    wrap.appendChild(video);
    card.appendChild(label);
    card.appendChild(wrap);
    return card;
  };

  const attachPoseOverlay = (block, poseSrc, caseBase, poseVideoEl) => {
    if (!block || !poseSrc || !poseVideoEl) return;
    const poseUrl = resolveUrl(caseBase, poseSrc);
    const wraps = Array.from(block.querySelectorAll(".compare-output .portrait-video"));
    if (!wraps.length) return;

    const pairs = wraps
      .map((wrap) => {
        if (!wrap) return null;

        const baseVideo = wrap.querySelector("video:not(.pose-overlay-video)");
        if (!baseVideo) return null;

        let overlay = wrap.querySelector(".pose-overlay-video");
        if (!overlay) {
          overlay = document.createElement("video");
          overlay.className = "pose-overlay-video";
          overlay.muted = true;
          overlay.loop = true;
          overlay.playsInline = true;
          overlay.preload = "none";
          setDeferredVideoSource(overlay, poseUrl, "video/mp4");
          wrap.appendChild(overlay);
        }

        return { baseVideo, overlay };
      })
      .filter(Boolean);

    if (!pairs.length) return;

    const getAlignedTime = (t, dur) => {
      const tt = Number.isFinite(t) && t >= 0 ? t : 0;
      const d = Number.isFinite(dur) && dur > 0 ? dur : 0;
      if (!d) return tt;
      const m = tt % d;
      return m < 0 ? m + d : m;
    };

    const getMasterTime = () => {
      const candidate = pairs.find((p) => p && p.baseVideo && p.baseVideo.readyState >= 1) || pairs[0];
      if (!candidate || !candidate.baseVideo) return 0;
      return candidate.baseVideo.currentTime || 0;
    };

    const syncOverlays = () => {
      if (!block.classList.contains("pose-overlay-active")) return;
      const t = getMasterTime();

      if (poseVideoEl && poseVideoEl.readyState >= 1) {
        const target = getAlignedTime(t, poseVideoEl.duration);
        const dt = Math.abs((poseVideoEl.currentTime || 0) - target);
        if (dt > 0.12) {
          try {
            poseVideoEl.currentTime = target;
          } catch (_) {}
        }
      }

      pairs.forEach((p) => {
        if (!p || !p.overlay || !p.baseVideo) return;
        if (p.overlay.readyState < 1) return;
        const target = getAlignedTime(p.baseVideo.currentTime || 0, p.overlay.duration);
        const dt = Math.abs((p.overlay.currentTime || 0) - target);
        if (dt > 0.12) {
          try {
            p.overlay.currentTime = target;
          } catch (_) {}
        }

        if (p.baseVideo.paused) {
          try {
            p.overlay.pause();
          } catch (_) {}
        } else {
          try {
            const playPromise = p.overlay.play();
            if (playPromise && typeof playPromise.catch === "function") playPromise.catch(() => {});
          } catch (_) {}
        }
      });
    };

    const playOverlays = () => {
      block.classList.add("pose-overlay-active");
      ensureVideoSourceLoaded(poseVideoEl);
      syncOverlays();
      try {
        playVideoSafely(poseVideoEl);
      } catch (_) {}
      pairs.forEach((p) => {
        if (!p || !p.overlay) return;
        ensureVideoSourceLoaded(p.overlay);
        playVideoSafely(p.overlay);
      });
    };

    const stopOverlays = () => {
      block.classList.remove("pose-overlay-active");
      pauseVideoSafely(poseVideoEl);
      pairs.forEach((p) => {
        if (!p || !p.overlay) return;
        pauseVideoSafely(p.overlay);
      });
    };

    const hoverTarget = poseVideoEl.closest(".portrait-video") || poseVideoEl;
    hoverTarget.addEventListener("mouseenter", playOverlays);
    hoverTarget.addEventListener("mouseleave", stopOverlays);
    pairs.forEach((p) => {
      if (!p || !p.baseVideo) return;
      p.baseVideo.addEventListener("timeupdate", syncOverlays);
      p.baseVideo.addEventListener("seeked", syncOverlays);
      p.baseVideo.addEventListener("playing", syncOverlays);
      p.baseVideo.addEventListener("pause", syncOverlays);
    });
  };

  const reorderOutputsForSection = (sectionId, outputs) => {
    if (sectionId !== "r2v") return outputs;
    const ours = [];
    const others = [];
    (outputs || []).forEach((o) => {
      if ((o && (o.kind || "").toLowerCase()) === "ours") ours.push(o);
      else others.push(o);
    });

    const wanted = ["hunyuancustom", "humo", "vace", "phantom"];
    const rank = (o) => {
      const label = ((o && o.label) || "").toLowerCase();
      for (let i = 0; i < wanted.length; i += 1) {
        if (label.includes(wanted[i])) return i;
      }
      return wanted.length;
    };
    others.sort((a, b) => rank(a) - rank(b));
    return ours.concat(others);
  };

  const renderCaseBlock = async (sectionId, caseName, manifest, showInputsLabel) => {
    const caseBase = `${TASKS_BASE}${sectionId}/${caseName}/`;
    const block = document.createElement("div");
    block.className = "compare-block compare-block-fullbleed";

    const aside = document.createElement("aside");
    aside.className = "compare-input";

    if (showInputsLabel) {
      const title = document.createElement("div");
      title.className = "compare-input-title";
      title.textContent = "Inputs";
      aside.appendChild(title);
    }

    const inputs = (manifest && manifest.inputs) || {};
    if (inputs.text) {
      try {
        const t = await fetchText(resolveUrl(caseBase, inputs.text));
        aside.appendChild(createTextCard(t));
      } catch (_) {}
    }

    if (inputs.audio) {
      aside.appendChild(createAudioCard(inputs.audio, caseBase));
    }

    const hasRefs = Array.isArray(inputs.refs) && inputs.refs.length;
    const hasPose = !!inputs.pose;
    let poseVideoEl = null;
    if (hasPose) {
      const row = document.createElement("div");
      row.className = "input-row";
      if (hasRefs) row.appendChild(createRefCard(inputs.refs, caseBase));
      const poseCard = createPoseCard(inputs.pose, caseBase);
      poseVideoEl = poseCard.querySelector("video");
      row.appendChild(poseCard);
      aside.appendChild(row);
    } else if (hasRefs) {
      aside.appendChild(createRefCard(inputs.refs, caseBase));
    }

    const outputWrap = document.createElement("div");
    outputWrap.className = "compare-output";
    const outputRow = document.createElement("div");
    outputRow.className = "output-row";
    reorderOutputsForSection(sectionId, manifest.outputs || []).forEach((o) =>
      outputRow.appendChild(createVideoCard(o, caseBase, caseName))
    );
    outputWrap.appendChild(outputRow);

    block.appendChild(aside);
    block.appendChild(outputWrap);
    if (hasPose && poseVideoEl) attachPoseOverlay(block, inputs.pose, caseBase, poseVideoEl);
    return block;
  };

  const getInputsLabelQuota = (sectionId) => (sectionId === "rap2v" ? 2 : 1);

  const shouldShowInputsLabelForCase = (sectionId, caseIndex) => caseIndex < getInputsLabelQuota(sectionId);

  const createPlaceholderCard = (className) => {
    const card = document.createElement("div");
    card.className = className;
    const shimmer = document.createElement("div");
    shimmer.className = "placeholder-shimmer";
    card.appendChild(shimmer);
    return card;
  };

  const createCasePlaceholder = (sectionId, caseName, caseIndex) => {
    const block = document.createElement("div");
    block.className = "compare-block compare-block-fullbleed compare-block-placeholder";
    block.dataset.sectionId = sectionId;
    block.dataset.caseName = caseName;
    block.dataset.caseIndex = String(caseIndex);

    const aside = document.createElement("aside");
    aside.className = "compare-input";

    if (shouldShowInputsLabelForCase(sectionId, caseIndex)) {
      const title = document.createElement("div");
      title.className = "compare-input-title";
      title.textContent = "Inputs";
      aside.appendChild(title);
    }

    const textCard = document.createElement("div");
    textCard.className = "input-card input-card-placeholder";
    const textLabel = document.createElement("div");
    textLabel.className = "input-label";
    textLabel.textContent = "Text";
    textCard.appendChild(textLabel);
    textCard.appendChild(createPlaceholderCard("placeholder-block placeholder-block-text"));
    aside.appendChild(textCard);

    const mediaRow = document.createElement("div");
    mediaRow.className = "input-row";
    const refsCard = document.createElement("div");
    refsCard.className = "input-card input-card-ref input-card-placeholder";
    const refsLabel = document.createElement("div");
    refsLabel.className = "input-label";
    refsLabel.textContent = "Reference Images";
    refsCard.appendChild(refsLabel);
    const refsGrid = document.createElement("div");
    refsGrid.className = "ref-grid ref-grid-placeholder";
    refsGrid.appendChild(createPlaceholderCard("ref-img ref-img-placeholder"));
    refsGrid.appendChild(createPlaceholderCard("ref-img ref-img-placeholder"));
    refsCard.appendChild(refsGrid);
    mediaRow.appendChild(refsCard);

    const poseCard = document.createElement("div");
    poseCard.className = "input-card input-card-pose input-card-placeholder";
    const poseLabel = document.createElement("div");
    poseLabel.className = "input-label";
    poseLabel.textContent = "Preview";
    poseCard.appendChild(poseLabel);
    poseCard.appendChild(createPlaceholderCard("portrait-video portrait-video-input placeholder-video"));
    mediaRow.appendChild(poseCard);
    aside.appendChild(mediaRow);

    const outputWrap = document.createElement("div");
    outputWrap.className = "compare-output";
    const outputRow = document.createElement("div");
    outputRow.className = "output-row";

    for (let i = 0; i < 3; i += 1) {
      const videoCard = document.createElement("div");
      videoCard.className = "video-card video-card-placeholder";
      videoCard.appendChild(createPlaceholderCard("video-label placeholder-label"));
      videoCard.appendChild(createPlaceholderCard("portrait-video portrait-video-xl placeholder-video"));
      outputRow.appendChild(videoCard);
    }

    outputWrap.appendChild(outputRow);
    block.appendChild(aside);
    block.appendChild(outputWrap);
    return block;
  };

  let lazyCaseObserver = null;
  const ensureLazyCaseObserver = () => {
    if (lazyCaseObserver || !("IntersectionObserver" in window)) return lazyCaseObserver;
    lazyCaseObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const placeholder = entry.target;
          const load = placeholder && placeholder.__loadCaseBlock;
          lazyCaseObserver.unobserve(placeholder);
          if (typeof load === "function") load();
        });
      },
      { rootMargin: "700px 0px", threshold: 0.01 }
    );
    return lazyCaseObserver;
  };

  const registerLazyCaseEntry = (entry, sectionEl) => {
    if (!entry || !entry.placeholder || entry.block) return;
    entry.placeholder.__loadCaseBlock = () => hydrateLazyCaseEntry(entry, sectionEl);
    const observer = ensureLazyCaseObserver();
    if (observer) observer.observe(entry.placeholder);
    else hydrateLazyCaseEntry(entry, sectionEl).catch(() => {});
  };

  const hydrateLazyCaseEntry = async (entry, sectionEl) => {
    if (!entry || entry.block || entry.hydrating) return;
    entry.hydrating = true;
    try {
      const manifest = await fetchJson(`${TASKS_BASE}${entry.sectionId}/${entry.caseName}/manifest.json`);
      const block = await renderCaseBlock(
        entry.sectionId,
        entry.caseName,
        manifest,
        shouldShowInputsLabelForCase(entry.sectionId, entry.caseIndex)
      );
      entry.block = block;
      if (entry.currentEl && entry.currentEl.isConnected) {
        entry.currentEl.replaceWith(block);
      }
      entry.currentEl = block;
      enableHoverControls(sectionEl);
      enableLazyAutoplay(sectionEl);
      enableAutoScrollText(sectionEl);
      enableInputFade(sectionEl);
    } catch (_) {
      if (entry.placeholder && entry.placeholder.isConnected) {
        entry.placeholder.classList.add("compare-block-error");
      }
    } finally {
      entry.hydrating = false;
    }
  };

  const createLazyCaseEntry = (sectionId, caseName, caseIndex) => {
    const placeholder = createCasePlaceholder(sectionId, caseName, caseIndex);
    return {
      sectionId,
      caseName,
      caseIndex,
      placeholder,
      block: null,
      currentEl: placeholder,
      hydrating: false,
    };
  };

  const attachEntriesToStack = (stack, entries, beforeEl, sectionEl) => {
    entries.forEach((entry) => {
      const node = entry.currentEl || entry.block || entry.placeholder;
      if (!node) return;
      stack.insertBefore(node, beforeEl || null);
      entry.currentEl = node;
      if (!entry.block) registerLazyCaseEntry(entry, sectionEl);
    });
  };

  const hydrateTaskSection = async (sectionEl, sections) => {
    if (!sectionEl || sectionEl.dataset.taskHydrated === "true" || sectionEl.dataset.taskHydrating === "true") return;
    sectionEl.dataset.taskHydrating = "true";

    const sectionId = sectionEl.id;
    const cases = Array.isArray(sections[sectionId]) ? sections[sectionId] : [];
    if (!cases.length) {
      sectionEl.dataset.taskHydrated = "true";
      sectionEl.dataset.taskHydrating = "false";
      return;
    }

    const stack = document.createElement("div");
    stack.className = "compare-stack";

    const body = sectionEl.querySelector(".task-body");
    if (!body) {
      sectionEl.dataset.taskHydrating = "false";
      return;
    }
    body.innerHTML = "";
    body.appendChild(stack);
    sectionEl.dataset.dynamicRendered = "true";

    const collapseLimit = getCasesCollapseLimit(sectionId);
    const shouldCollapse = cases.length > collapseLimit;
    const firstBatch = shouldCollapse ? cases.slice(0, collapseLimit) : cases;
    const restBatch = shouldCollapse ? cases.slice(collapseLimit) : [];
    const firstEntries = firstBatch.map((caseName, index) => createLazyCaseEntry(sectionId, caseName, index));
    attachEntriesToStack(stack, firstEntries, null, sectionEl);

    if (!shouldCollapse || !firstEntries.length) {
      sectionEl.dataset.taskHydrated = "true";
      sectionEl.dataset.taskHydrating = "false";
      return;
    }

    const toggleWrap = document.createElement("div");
    toggleWrap.className = "compare-toggle";
    const toggleBtn = document.createElement("button");
    toggleBtn.type = "button";
    toggleBtn.className = "compare-toggle-btn";
    toggleBtn.textContent = "See More";
    toggleBtn.setAttribute("aria-expanded", "false");
    toggleWrap.appendChild(toggleBtn);
    stack.appendChild(toggleWrap);
    const restEntries = restBatch.map((caseName, index) =>
      createLazyCaseEntry(sectionId, caseName, firstBatch.length + index)
    );

    let expanded = false;
    let busy = false;

    const collapse = () => {
      restEntries.forEach((entry) => {
        const node = entry.currentEl;
        if (node && node.parentNode === stack) stack.removeChild(node);
      });
      expanded = false;
      toggleBtn.textContent = "See More";
      toggleBtn.setAttribute("aria-expanded", "false");
    };

    const expand = async () => {
      if (!restEntries.length) return;
      busy = true;
      toggleBtn.disabled = true;
      toggleBtn.textContent = "Loading…";
      attachEntriesToStack(stack, restEntries, toggleWrap, sectionEl);
      enableHoverControls(sectionEl);
      enableLazyAutoplay(sectionEl);
      enableAutoScrollText(sectionEl);
      enableInputFade(sectionEl);

      expanded = true;
      toggleBtn.disabled = false;
      toggleBtn.textContent = "See Less";
      toggleBtn.setAttribute("aria-expanded", "true");
      busy = false;
    };

    toggleBtn.addEventListener("click", async () => {
      if (busy) return;
      if (!expanded) {
        await expand();
      } else {
        collapse();
      }
    });

    sectionEl.dataset.taskHydrated = "true";
    sectionEl.dataset.taskHydrating = "false";
  };

  const hydrateTaskSections = async () => {
    const els = Array.from(document.querySelectorAll(".task-section")).filter((el) => TASK_SECTION_IDS.includes(el.id));
    if (!els.length) return;

    let sectionsPromise = null;
    const getSections = () => {
      if (!sectionsPromise) sectionsPromise = loadTasksIndex();
      return sectionsPromise;
    };

    const hydrateOne = async (sectionEl) => {
      const sections = await getSections();
      await hydrateTaskSection(sectionEl, sections);
    };

    if (!("IntersectionObserver" in window)) {
      await Promise.all(els.map((sectionEl) => hydrateOne(sectionEl)));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const sectionEl = entry.target;
          observer.unobserve(sectionEl);
          hydrateOne(sectionEl).catch(() => {});
        });
      },
      { rootMargin: "700px 0px", threshold: 0.01 }
    );

    els.forEach((sectionEl) => observer.observe(sectionEl));
  };

  const enableHeroTeaser = () => {
    const titleEl = document.querySelector(".hero-title");
    const teaserEl = document.getElementById("heroTeaser");

    if (!titleEl || !teaserEl) return;

    const updateWidth = () => {
      const titleWidth = titleEl.getBoundingClientRect().width;
      if (!titleWidth) return;
      teaserEl.style.width = `${Math.round(titleWidth * 0.75)}px`;
    };

    updateWidth();
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(updateWidth).catch(() => {});
    }
    window.addEventListener("resize", () => requestAnimationFrame(updateWidth));
  };

  const enableHeroVideoControls = () => {
    const video = document.getElementById("heroTeaserVideo");
    const wrap = document.getElementById("heroTeaser");
    const playBtn = document.getElementById("heroVideoPlayBtn");
    const replayBtn = document.getElementById("heroVideoReplayBtn");
    if (!video || !wrap || !playBtn || !replayBtn) return;

    let hasStarted = false;

    // Ensure the hero video is eagerly loaded but not auto-started.
    try {
      video.removeAttribute("autoplay");
      video.removeAttribute("loop");
      video.autoplay = false;
      video.loop = false;
      video.preload = "auto";
    } catch (_) {}

    pauseVideoSafely(video);
    try {
      video.load();
    } catch (_) {}

    const showPlay = () => {
      if (hasStarted) return;
      playBtn.hidden = false;
      replayBtn.hidden = true;
      wrap.classList.add("hero-video-idle");
      try {
        video.controls = false;
      } catch (_) {}
    };

    const showReplay = () => {
      playBtn.hidden = true;
      replayBtn.hidden = false;
      wrap.classList.add("hero-video-idle");
      try {
        video.controls = false;
      } catch (_) {}
    };

    const hideAll = () => {
      playBtn.hidden = true;
      replayBtn.hidden = true;
      wrap.classList.remove("hero-video-idle");
    };

    const playNow = () => {
      hideAll();
      hasStarted = true;
      try {
        // Keep native controls (progress bar etc.) while playing.
        video.controls = true;
      } catch (_) {}
      try {
        const p = video.play();
        if (p && typeof p.catch === "function") {
          p.catch(() => {
            // If playback fails for any reason, fall back to showing play again.
            showPlay();
          });
        }
      } catch (_) {
        showPlay();
      }
    };

    showPlay();

    playBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      playNow();
    });

    replayBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      try {
        video.currentTime = 0;
      } catch (_) {}
      playNow();
    });

    video.addEventListener("play", () => {
      hideAll();
      hasStarted = true;
      try {
        video.controls = true;
      } catch (_) {}
    });
    video.addEventListener("ended", showReplay);
    video.addEventListener("pause", () => {
      if (video.ended) {
        showReplay();
        return;
      }
      // Mid-play pauses are handled by native controls; don't show overlays.
    });
  };

  const enableHoverControls = (root) => {
    const base = root || document;
    const allVideos = Array.from(base.querySelectorAll("video"));
    allVideos.forEach((video) => {
      if (video.dataset && video.dataset.hoverControlsBound === "true") return;
      if (video.dataset) video.dataset.hoverControlsBound = "true";
      video.addEventListener("mouseenter", () => {
        video.controls = true;
      });
      video.addEventListener("mouseleave", () => {
        if (video.dataset && video.dataset.keepControlsWhenPlaying === "true" && !video.paused) return;
        video.controls = false;
      });
    });
  };

  const enableAutoScrollText = (root) => {
    const base = root || document;
    const scrollers = Array.from(base.querySelectorAll('[data-autoscroll="true"]'));
    scrollers.forEach((el) => {
      if (el.dataset && el.dataset.autoScrollBound === "true") return;
      if (el.dataset) el.dataset.autoScrollBound = "true";
      let raf = 0;
      let isRunning = false;
      let phase = "down";
      let lastTs = 0;
      let pauseUntil = 0;

      const stop = () => {
        isRunning = false;
        phase = "down";
        lastTs = 0;
        pauseUntil = 0;
        if (raf) cancelAnimationFrame(raf);
        raf = 0;
        el.scrollTop = 0;
      };

      const tick = (ts) => {
        if (!isRunning) return;
        const max = Math.max(0, el.scrollHeight - el.clientHeight);
        if (max <= 2) {
          stop();
          return;
        }

        if (pauseUntil && ts < pauseUntil) {
          raf = requestAnimationFrame(tick);
          return;
        }

        if (!lastTs) lastTs = ts;
        const dt = ts - lastTs;
        lastTs = ts;

        const speed = 0.02;
        if (phase === "down") {
          el.scrollTop = Math.min(max, el.scrollTop + dt * speed);
          if (el.scrollTop >= max - 1) {
            el.scrollTop = max;
            phase = "done";
          }
        }

        raf = requestAnimationFrame(tick);
      };

      el.addEventListener("mouseenter", () => {
        if (isRunning) return;
        if (el.scrollHeight <= el.clientHeight + 2) return;
        isRunning = true;
        raf = requestAnimationFrame(tick);
      });

      el.addEventListener("mouseleave", stop);
    });
  };

  const enableInputFade = (root) => {
    const base = root || document;
    const els = Array.from(base.querySelectorAll(".input-text-scroll"));
    if (!els.length) return;

    const update = (el) => {
      const text = (el.textContent || "").trim();
      if (text) el.classList.add("has-fade");
      else el.classList.remove("has-fade");
    };

    els.forEach((el) => update(el));
  };

  let lazyVideoPreloadObserver = null;
  let lazyVideoPlaybackObserver = null;
  const enableLazyAutoplay = (root) => {
    const base = root || document;
    const videos = Array.from(base.querySelectorAll("video.lazy-video"));
    videos.forEach((v) => prepareDeferredVideoElement(v));
    if (!("IntersectionObserver" in window)) {
      videos.forEach((v) => playVideoSafely(v));
      return;
    }

    if (!lazyVideoPreloadObserver) {
      lazyVideoPreloadObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            ensureVideoSourceLoaded(entry.target);
          });
        },
        { rootMargin: "420px 0px", threshold: 0.01 }
      );
    }

    if (!lazyVideoPlaybackObserver) {
      lazyVideoPlaybackObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            const v = entry.target;
            if (entry.isIntersecting) {
              playVideoSafely(v);
            } else {
              pauseVideoSafely(v);
            }
          });
        },
        { threshold: 0.2 }
      );
    }

    videos.forEach((v) => {
      if (v.dataset && v.dataset.lazyVideoPreloadObserved !== "true") {
        v.dataset.lazyVideoPreloadObserved = "true";
        lazyVideoPreloadObserver.observe(v);
      }
      if (v.dataset && v.dataset.lazyVideoPlaybackObserved !== "true") {
        v.dataset.lazyVideoPlaybackObserved = "true";
        lazyVideoPlaybackObserver.observe(v);
      }
    });
  };

  const enableDropdown = () => {
    const dropdowns = Array.from(document.querySelectorAll(".dropdown"));
    dropdowns.forEach((dropdown) => {
      const btn = dropdown.querySelector(".dropbtn");
      if (!btn) return;

      btn.addEventListener("click", (event) => {
        const nav = document.querySelector(".top-nav");
        const collapsedNav = !!(nav && nav.classList.contains("is-collapsed"));
        if (window.innerWidth <= 768 || collapsedNav) {
          event.preventDefault();
          dropdown.classList.toggle("active");
        }
      });
    });

    document.addEventListener("click", (event) => {
      dropdowns.forEach((dropdown) => {
        if (dropdown.contains(event.target)) return;
        dropdown.classList.remove("active");
      });
    });
  };

  const enableTopNavResponsive = () => {
    const nav = document.querySelector(".top-nav");
    const inner = nav ? nav.querySelector(".top-nav-inner") : null;
    const left = nav ? nav.querySelector(".top-nav-left") : null;
    const actions = nav ? nav.querySelector(".top-nav-actions") : null;
    const toggle = document.getElementById("topNavMenuToggle");
    if (!nav || !inner || !left || !actions || !toggle) return;

    const closeMenu = () => {
      nav.classList.remove("is-menu-open");
      toggle.setAttribute("aria-expanded", "false");
    };

    const measureInlineWidth = (container) => {
      if (!container) return 0;
      const styles = getComputedStyle(container);
      const gap = parseFloat(styles.columnGap || styles.gap) || 0;
      const children = Array.from(container.children).filter((el) => {
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      });
      if (!children.length) return 0;
      const childWidth = children.reduce((sum, el) => sum + el.getBoundingClientRect().width, 0);
      return childWidth + gap * Math.max(0, children.length - 1);
    };

    const update = () => {
      const wasCollapsed = nav.classList.contains("is-collapsed");
      closeMenu();
      if (wasCollapsed) nav.classList.remove("is-collapsed");

      const innerStyles = getComputedStyle(inner);
      const innerGap = parseFloat(innerStyles.columnGap || innerStyles.gap) || 0;
      const leftContentWidth = measureInlineWidth(left);
      const actionsContentWidth = measureInlineWidth(actions);
      const shouldCollapse = leftContentWidth + actionsContentWidth + innerGap > inner.clientWidth;

      if (shouldCollapse) {
        nav.classList.add("is-collapsed");
      }
    };

    toggle.addEventListener("click", (event) => {
      event.preventDefault();
      const isOpen = nav.classList.toggle("is-menu-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    document.addEventListener("click", (event) => {
      if (nav.contains(event.target)) return;
      closeMenu();
    });

    window.addEventListener("resize", update, { passive: true });

    const ro = new ResizeObserver(update);
    ro.observe(inner);
    update();
  };

  const enableReplayAll = () => {
    const buttons = Array.from(document.querySelectorAll(".task-replay"));
    if (!buttons.length) return;

    const replayVideo = (video) => {
      if (!video) return;

      pauseVideoSafely(video);
      ensureVideoSourceLoaded(video);

      const playFromStart = () => {
        try {
          video.currentTime = 0;
        } catch (_) {}
        playVideoSafely(video);
      };

      if (video.readyState >= 1) {
        playFromStart();
        return;
      }

      video.addEventListener("loadedmetadata", playFromStart, { once: true });
      try {
        video.load();
      } catch (_) {}
    };

    const replayAllInSection = (sectionEl) => {
      const vids = Array.from(sectionEl.querySelectorAll("video"));
      vids.forEach((v) => {
        try {
          v.pause();
        } catch (_) {}
      });
      vids.forEach(replayVideo);
    };

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const section = btn.closest(".task-section");
        if (!section) return;
        replayAllInSection(section);
      });
    });
  };

  const enableNavTypewriter = () => {
    const titleEl = document.getElementById("navTaskTitle");
    if (!titleEl) return;

    const sections = Array.from(document.querySelectorAll(".task-section"));
    if (!sections.length) return;

    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const animateScrollTo = (toY, durationMs) =>
      new Promise((resolve) => {
        const startY = window.scrollY || window.pageYOffset || 0;
        const delta = toY - startY;
        if (Math.abs(delta) < 2 || durationMs <= 0 || prefersReducedMotion) {
          window.scrollTo(0, toY);
          resolve();
          return;
        }

        const ease = (t) => 1 - Math.pow(1 - t, 3);
        const start = performance.now();
        const step = (now) => {
          const t = Math.min(1, (now - start) / durationMs);
          window.scrollTo(0, Math.round(startY + delta * ease(t)));
          if (t < 1) {
            requestAnimationFrame(step);
            return;
          }
          resolve();
        };
        requestAnimationFrame(step);
      });

    const scrollToTarget = (targetId) => {
      if (!targetId) return;
      const nav = document.querySelector(".top-nav");
      const navOffset = (nav ? nav.offsetHeight : 0) + 10;

      if (targetId === "hero") {
        animateScrollTo(0, 420);
        return;
      }

      const target = document.getElementById(targetId);
      if (!target) return;
      const top = target.getBoundingClientRect().top + (window.scrollY || window.pageYOffset || 0) - navOffset;
      animateScrollTo(Math.max(0, top), 520);
    };

    const typewriter = (() => {
      let isRunning = false;
      let pending = null;
      let current = "";

      const set = async (target) => {
        const next = (target || "").trim();
        if (next === current) return;
        if (isRunning) {
          pending = next;
          return;
        }
        isRunning = true;
        pending = null;

        const deleteSpeed = 18;
        const typeSpeed = 26;
        const settlePause = 140;

        while (current.length) {
          current = current.slice(0, -1);
          titleEl.textContent = current;
          await sleep(deleteSpeed);
        }

        await sleep(settlePause);

        for (let i = 0; i < next.length; i += 1) {
          current += next[i];
          titleEl.textContent = current;
          await sleep(typeSpeed);
        }

        isRunning = false;

        if (pending !== null && pending !== current) {
          const p = pending;
          pending = null;
          set(p);
        }
      };

      const setImmediate = (t) => {
        current = (t || "").trim();
        pending = null;
        titleEl.textContent = current;
      };

      return { set, setImmediate };
    })();

    const getTitle = (el) => (el && el.dataset ? el.dataset.taskTitle || "" : "");
    const highlight = { text: "boundless creativity, with your multimodal inputs :\u00A0)", targetId: "gallery" };
    const featureItems = [
      { text: "Smooth Motion Quality", targetId: "mf-motion-quality" },
      { text: "Robust Physical Plausibility", targetId: "mf-physical-plausibility" },
      { text: "Native Long-Shot Generation", targetId: "mf-long-shot" },
      { text: "Expressive Avatar Animation", targetId: "mf-avatar-animation" },
      { text: "Stable Identity Preservation", targetId: "mf-alive" },
    ].filter((x) => x.text && x.targetId && document.getElementById(x.targetId));

    const items = []
      .concat(
        sections
          .map((s) => ({ text: getTitle(s).trim(), targetId: s.id || "" }))
          .filter((x) => x.text && x.targetId)
      )
      .concat(featureItems)
      .concat([highlight])
      .filter((x) => x.text && x.targetId)
      .filter((x, i, arr) => arr.findIndex((y) => y.text === x.text) === i);
    if (!items.length) return;

    let idx = 0;
    let activeTargetId = items[idx].targetId;
    titleEl.addEventListener("click", () => scrollToTarget(activeTargetId));

    typewriter.setImmediate("");
    typewriter.set(items[idx].text);

    if (items.length === 1) return;

    const intervalMs = 6000;
    window.setInterval(() => {
      idx = (idx + 1) % items.length;
      activeTargetId = items[idx].targetId;
      typewriter.set(items[idx].text);
    }, intervalMs);
  };

  const enableMediaLightbox = () => {
    const box = document.createElement("div");
    box.className = "media-lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.tabIndex = -1;

    const inner = document.createElement("div");
    inner.className = "media-lightbox-inner";

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "media-lightbox-close";
    closeBtn.setAttribute("aria-label", "Close");
    closeBtn.textContent = "×";

    inner.appendChild(closeBtn);
    box.appendChild(inner);
    document.body.appendChild(box);

    let isOpen = false;
    let lastActive = null;
    let silenced = null;

    const restoreSilenced = () => {
      if (!Array.isArray(silenced)) return;
      silenced.forEach((x) => {
        const el = x.el;
        if (!el) return;
        try {
          el.muted = x.muted;
        } catch (_) {}
        if (typeof x.volume === "number") {
          try {
            el.volume = x.volume;
          } catch (_) {}
        }
        if (typeof x.currentTime === "number") {
          try {
            el.currentTime = x.currentTime;
          } catch (_) {}
        }
        if (x.wasPlaying) {
          try {
            const p = el.play();
            if (p && typeof p.catch === "function") p.catch(() => {});
          } catch (_) {}
        }
      });
      silenced = null;
    };

    const silenceOthers = () => {
      restoreSilenced();
      silenced = [];
      const medias = Array.from(document.querySelectorAll("video, audio")).filter((el) => !el.closest(".media-lightbox"));
      medias.forEach((el) => {
        silenced.push({
          el,
          muted: !!el.muted,
          volume: typeof el.volume === "number" ? el.volume : undefined,
          currentTime: typeof el.currentTime === "number" ? el.currentTime : undefined,
          wasPlaying: !el.paused,
        });
        try {
          el.muted = true;
        } catch (_) {}
        if (el.tagName === "AUDIO") {
          try {
            el.pause();
          } catch (_) {}
        }
      });
    };

    const close = () => {
      if (!isOpen) return;
      isOpen = false;
      document.body.classList.remove("has-lightbox");
      box.classList.remove("is-open");
      const media = inner.querySelector(".media-lightbox-media");
      if (media && media.tagName === "VIDEO") {
        try {
          media.pause();
        } catch (_) {}
      }
      if (media) media.remove();
      restoreSilenced();
      if (lastActive && typeof lastActive.focus === "function") lastActive.focus();
    };

    const openWith = (media) => {
      const prev = inner.querySelector(".media-lightbox-media");
      if (prev) prev.remove();
      lastActive = document.activeElement;
      inner.appendChild(media);
      document.body.classList.add("has-lightbox");
      box.classList.add("is-open");
      isOpen = true;
      box.focus();
    };

    const openImg = (imgEl) => {
      const src = imgEl.currentSrc || imgEl.src;
      if (!src) return;
      const img = document.createElement("img");
      img.className = "media-lightbox-media";
      img.src = src;
      img.alt = imgEl.alt || "";
      openWith(img);
    };

    const openVideo = (videoEl) => {
      const src =
        videoEl.currentSrc ||
        videoEl.dataset.src ||
        (videoEl.querySelector("source") && videoEl.querySelector("source").src) ||
        "";
      if (!src) return;
      silenceOthers();
      const v = document.createElement("video");
      v.className = "media-lightbox-media";
      v.controls = true;
      v.playsInline = true;
      v.preload = "metadata";
      v.loop = !!videoEl.loop;
      v.muted = false;
      v.setAttribute("controlslist", "nodownload noplaybackrate noremoteplayback");
      const s = document.createElement("source");
      s.src = src;
      s.type = "video/mp4";
      v.appendChild(s);
      if (videoEl.currentTime) {
        v.addEventListener(
          "loadedmetadata",
          () => {
            try {
              v.currentTime = videoEl.currentTime;
            } catch (_) {}
          },
          { once: true }
        );
      }
      openWith(v);
      const p = v.play();
      if (p && typeof p.catch === "function") {
        p.catch(() => {
          try {
            v.muted = true;
          } catch (_) {}
          v.play().catch(() => {});
        });
      }
    };

    closeBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      close();
    });

    box.addEventListener("click", (e) => {
      if (inner.contains(e.target) && e.target !== box) return;
      close();
    });

    document.addEventListener("keydown", (e) => {
      if (!isOpen) return;
      if (e.key === "Escape") close();
    });

    document.addEventListener("click", (e) => {
      const t = e.target;
      if (!t || !(t instanceof Element)) return;
      const el = t.closest("img, video");
      if (!el) return;
      if (el.closest(".media-lightbox")) return;
      if (!el.closest("main")) return;
      if (el.tagName === "IMG") {
        e.preventDefault();
        openImg(el);
      } else if (el.tagName === "VIDEO") {
        e.preventDefault();
        openVideo(el);
      }
    });
  };

  const enableBackToTop = () => {
    const btn = document.getElementById("back-to-top");
    if (!btn) return;

    const thresholdPx = 360;
    const update = () => {
      if (window.scrollY > thresholdPx) btn.classList.add("is-visible");
      else btn.classList.remove("is-visible");
    };

    update();
    window.addEventListener("scroll", update, { passive: true });
    btn.addEventListener("click", () => {
      const reduceMotion =
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      try {
        window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      } catch (_) {
        window.scrollTo(0, 0);
      }
    });
  };

  const enableMoreFeaturesLayout = () => {
    const blocks = Array.from(document.querySelectorAll(".mf-animation"));
    if (!blocks.length) return;

    const ro = new ResizeObserver(() => {
      blocks.forEach((el) => {
        if (!el.isConnected) return;
        const portrait = el.querySelector(".mf-animation-portrait");
        const grid = el.querySelector(".mf-animation-grid");
        if (!portrait || !grid) return;
        const gridHeight = grid.getBoundingClientRect().height;
        if (!Number.isFinite(gridHeight) || gridHeight <= 0) return;

        const portraitHeight = gridHeight;
        const portraitWidth = (portraitHeight * 9) / 16;

        el.style.setProperty("--mf-animation-portrait-h", `${portraitHeight.toFixed(2)}px`);
        el.style.setProperty("--mf-animation-portrait-w", `${portraitWidth.toFixed(2)}px`);
      });
    });

    blocks.forEach((el) => ro.observe(el));
  };

  const enableMoreFeaturesAutoFit = () => {
    const section = document.querySelector(".section-more-features");
    const grid = document.querySelector(".more-features-grid");
    if (!section || !grid || !grid.parentElement) return;

    const parent = grid.parentElement;
    const ro = new ResizeObserver(() => {
      const availableWidth = parent.clientWidth;
      const currentScale = parseFloat(getComputedStyle(section).getPropertyValue("--mf-scale")) || 1;
      const naturalGridWidth = grid.scrollWidth / currentScale;
      if (!naturalGridWidth || !availableWidth) return;

      const scale = Math.min(1, availableWidth / naturalGridWidth);
      section.style.setProperty("--mf-scale", scale.toString());
    });

    ro.observe(parent);
  };

  const enableTaskAutoFit = () => {
    const taskSections = document.querySelectorAll(".task-section");

    taskSections.forEach((section) => {
      const ro = new ResizeObserver(() => {
        const body = section.querySelector(".task-body");
        const stack = section.querySelector(".compare-stack");
        if (!body || !stack) return;

        const containerWidth = section.clientWidth;
        const currentCompareScale = parseFloat(getComputedStyle(section).getPropertyValue("--compare-scale")) || 1;
        const scaledStackWidth = stack.scrollWidth;
        const naturalStackWidth = scaledStackWidth / currentCompareScale;

        let compareScale = 1;
        if (naturalStackWidth > 0 && containerWidth > 0) {
          compareScale = containerWidth / (naturalStackWidth + 36);
          if (compareScale > 1) compareScale = 1;
        }
        
        let scaleChanged = false;
        if (Math.abs(compareScale - currentCompareScale) > 0.005) {
          section.style.setProperty("--compare-scale", compareScale.toString());
          scaleChanged = true;
        }

        const labels = section.querySelectorAll(".compare-input-title, .video-label");

        labels.forEach((label) => {
          label.style.setProperty("--fit-scale", "1");
          const availableWidth = label.clientWidth;
          const naturalLabelWidth = label.scrollWidth;
          let fitScale = 1;

          if (availableWidth > 0 && naturalLabelWidth > availableWidth) {
            // Keep a readable lower bound; below that we fall back to ellipsis.
            fitScale = Math.max(0.78, availableWidth / naturalLabelWidth);
          }

          const currentFitScale = parseFloat(getComputedStyle(label).getPropertyValue("--fit-scale")) || 1;
          if (Math.abs(fitScale - currentFitScale) > 0.005 || scaleChanged) {
            label.style.setProperty("--fit-scale", fitScale.toString());
          }
        });
      });
      ro.observe(section);
    });
  };
  const enableGalleryAutoFit = () => {
    const grid = document.querySelector(".gallery-grid");
    const strip = document.querySelector(".gallery-strip");
    if (!grid || !strip) return;

    let naturalStripWidth = 0;

    const ro = new ResizeObserver(() => {
      if (naturalStripWidth === 0) {
        // Measure it the first time without any scaling
        grid.style.setProperty("--gallery-scale", "1");
        naturalStripWidth = strip.scrollWidth;
      }

      const containerWidth = grid.clientWidth;
      if (naturalStripWidth > 0 && containerWidth > 0) {
        const scale = Math.min(1, containerWidth / naturalStripWidth);
        grid.style.setProperty("--gallery-scale", scale.toString());
      }
    });
    ro.observe(grid);
  };

  document.addEventListener("DOMContentLoaded", async () => {
    enableLazyAutoplay();
    try {
      await hydrateTaskSections();
    } catch (_) {}
    enableHeroTeaser();
    enableHeroVideoControls();
    enableHoverControls();
    enableMediaLightbox();
    enableAutoScrollText();
    enableInputFade();
    enableDropdown();
    enableTopNavResponsive();
    enableReplayAll();
    enableNavTypewriter();
    enableBackToTop();
    enableMoreFeaturesLayout();
    enableMoreFeaturesAutoFit();
    enableGalleryAutoFit();
    enableTaskAutoFit();
  });
})();
