import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS3DRenderer, CSS3DObject } from 'three/addons/renderers/CSS3DRenderer.js';

const CONFIG = {
  terminal: {
    width: 7.5,
    height: 4.9,
    depth: 0.08,
    cornerRadius: 0.3,
  },
  titleBar: {
    width: 7.35,
    height: 0.5,
    depth: 0.02,
  },
  display: {
    width: 7.3,
    height: 4.25,
    cornerRadius: 0.25,
  },
  buttons: {
    radius: 0.1,
    spacing: 0.35,
    startX: 0.4,
    colors: {
      close: 0xff3b30,
      minimize: 0xffc107,
      maximize: 0x28cd41,
    },
  },
  textScale: 0.0103,
  zIndex: {
    frame: 0,
    titleBar: 0.09,
    display: 0.09,
    buttons: 0.13,
    text: 0.11,
  },
  camera: {
    fov: 35,
    near: 0.1,
    far: 1000,
    position: { x: 4, y: 0.5, z: 9 },
    rotateSpeed: 0.3,
    terminalOffsetX: 0,
  },
  colors: {
    black: 0x0d0d0d,
    surface: 0x1a1a1a,
    border: 0x2a2a2a,
    accent: 0xccff00,
  },
  animation: {
    rotationSpeed: 0.01,
    rotationAmplitude: { y: 0.02, x: 0.01 },
  },
  responsive: {
    referenceWidth: 850,
    referenceHeight: 480,
    rotationClearance: 0.75,
    scaleMin: 0.5,
    scaleMax: 0.8,
    groundPositionMultiplier: -2,
  },
};

const TERMINAL_DATA_HERO = {
  command: '$ quadro list --milestone "API Development"',
  headers: ['Milestone', 'ID', 'Title', 'Status'],
  rows: [
    { milestone: 'API Development', id: 42, title: 'Design REST endpoints', status: '✓ done' },
    { milestone: 'API Development', id: 43, title: 'Implement auth layer', status: '✓ done' },
    { milestone: 'API Development', id: 44, title: 'Add rate limiting', status: '✓ done' },
    { milestone: 'API Development', id: 45, title: 'Write integration tests', status: 'progress' },
  ],
};

const TERMINAL_DATA_MCP = {
  messages: [
    { role: 'input_box_start' },
    { role: 'prompt', text: '>' },
    { role: 'user_input', text: 'Start task #42 using Quadro' },
    { role: 'input_box_end' },
    { role: 'loading', text: '✶ Razzle-dazzling…' },
    {
      role: 'tool_use',
      name: 'mcp__quadro__start_task',
      params: { task_id: 42 }
    },
    {
      role: 'tool_result',
      name: 'mcp__quadro__start_task',
      content: 'Task #42 marked as in progress'
    },
    { role: 'assistant', text: 'Task started! I\'ll help you implement the REST endpoints.' },
  ],
};

const TERMINAL_COLORS = {
  command: '#ccff00',
  border: '#ffffff',
  header: '#9e6ffe',
  milestone: '#5e7175',
  id: '#fd971e',
  done: '#ccff00',
  progress: '#ffffff',
};

/**
 * @param {string} text
 * @returns {string}
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function createRoundedRectShape(width, height, radius, corners = {}) {
  const {
    topLeft = true,
    topRight = true,
    bottomLeft = true,
    bottomRight = true,
  } = corners;

  const shape = new THREE.Shape();
  const halfWidth = width / 2;
  const halfHeight = height / 2;

  shape.moveTo(-halfWidth, -halfHeight + (bottomLeft ? radius : 0));
  shape.lineTo(-halfWidth, halfHeight - (topLeft ? radius : 0));

  if (topLeft) {
    shape.quadraticCurveTo(-halfWidth, halfHeight, -halfWidth + radius, halfHeight);
  } else {
    shape.lineTo(-halfWidth, halfHeight);
  }

  shape.lineTo(halfWidth - (topRight ? radius : 0), halfHeight);

  if (topRight) {
    shape.quadraticCurveTo(halfWidth, halfHeight, halfWidth, halfHeight - radius);
  } else {
    shape.lineTo(halfWidth, halfHeight);
  }

  shape.lineTo(halfWidth, -halfHeight + (bottomRight ? radius : 0));

  if (bottomRight) {
    shape.quadraticCurveTo(halfWidth, -halfHeight, halfWidth - radius, -halfHeight);
  } else {
    shape.lineTo(halfWidth, -halfHeight);
  }

  shape.lineTo(-halfWidth + (bottomLeft ? radius : 0), -halfHeight);

  if (bottomLeft) {
    shape.quadraticCurveTo(-halfWidth, -halfHeight, -halfWidth, -halfHeight + radius);
  } else {
    shape.lineTo(-halfWidth, -halfHeight);
  }

  return shape;
}

class TableContent {
  constructor(data) {
    this.data = data;
    this.widths = [15, 2, 23, 8];
  }

  buildBorder(left, middle, right) {
    const segments = this.widths.map(w => '─'.repeat(w + 2));
    return left + segments.join(middle) + right;
  }

  colorize(text, color) {
    return color ? `<span style="color: ${color};">${text}</span>` : text;
  }

  render() {
    const { command, headers, rows } = this.data;

    const topBorder = this.buildBorder('┌', '┬', '┐');
    const separator = this.buildBorder('├', '┼', '┤');
    const bottomBorder = this.buildBorder('└', '┴', '┘');

    const headerRow = headers.map((h, i) =>
      this.colorize(escapeHtml(h.padEnd(this.widths[i])), TERMINAL_COLORS.header)
    ).join(' │ ');

    const dataRows = rows.map(row => {
      const cells = [
        this.colorize(escapeHtml(row.milestone.padEnd(this.widths[0])), TERMINAL_COLORS.milestone),
        this.colorize(escapeHtml(String(row.id).padEnd(this.widths[1])), TERMINAL_COLORS.id),
        escapeHtml(row.title.padEnd(this.widths[2])),
        this.colorize(
          escapeHtml(row.status.padEnd(this.widths[3])),
          row.status === 'progress' ? TERMINAL_COLORS.progress : TERMINAL_COLORS.done
        ),
      ];
      return `│ ${cells.join(' │ ')} │`;
    }).join('\n');

    return `${this.colorize(escapeHtml(command), TERMINAL_COLORS.command)}

${this.colorize(topBorder, TERMINAL_COLORS.border)}
${this.colorize(`│ ${headerRow} │`, TERMINAL_COLORS.border)}
${this.colorize(separator, TERMINAL_COLORS.border)}
${this.colorize(dataRows, TERMINAL_COLORS.border)}
${this.colorize(bottomBorder, TERMINAL_COLORS.border)}`;
  }
}

class ConversationContent {
  constructor(data) {
    this.data = data;
  }

  formatToolParams(params) {
    return JSON.stringify(params, null, 2);
  }

  formatToolContent(content) {
    if (typeof content === 'object') {
      return JSON.stringify(content, null, 2);
    }
    return content;
  }

  render() {
    const { messages } = this.data;
    const lines = [];
    const blueBorder = '─'.repeat(65);

    messages.forEach((msg) => {
      if (msg.role === 'input_box_start') {
        lines.push(`<span style="color: #4a9eff;">${blueBorder}</span>`);
      } else if (msg.role === 'input_box_end') {
        lines.push(`<span style="color: #4a9eff;">${blueBorder}</span>`);
      } else if (msg.role === 'prompt') {
        lines.push(`<span style="color: ${TERMINAL_COLORS.border};">${escapeHtml(msg.text)}</span>`);
      } else if (msg.role === 'user_input') {
        if (lines.length > 0) {
          lines[lines.length - 1] += ` ${escapeHtml(msg.text)}`;
        }
      } else if (msg.role === 'loading') {
        lines.push(`\n<span style="color: ${TERMINAL_COLORS.accent};">${escapeHtml(msg.text)}</span>`);
      } else if (msg.role === 'thinking') {
        lines.push(`\n<span style="color: ${TERMINAL_COLORS.milestone};">${escapeHtml(msg.text)}</span>`);
      } else if (msg.role === 'assistant') {
        lines.push(`\n<span style="color: ${TERMINAL_COLORS.border};">${escapeHtml(msg.text)}</span>`);
      } else if (msg.role === 'tool_use') {
        const params = this.formatToolParams(msg.params);
        lines.push(`\n<span style="color: ${TERMINAL_COLORS.milestone};">Using tool:</span> <span style="color: ${TERMINAL_COLORS.id};">${escapeHtml(msg.name)}</span>`);
        lines.push(`<span style="color: ${TERMINAL_COLORS.milestone};">${escapeHtml(params)}</span>`);
      } else if (msg.role === 'tool_result') {
        const content = this.formatToolContent(msg.content);
        lines.push(`\n<span style="color: ${TERMINAL_COLORS.done};">✓</span> <span style="color: ${TERMINAL_COLORS.milestone};">${escapeHtml(msg.name)}</span>`);
        lines.push(`<span style="color: ${TERMINAL_COLORS.done};">${escapeHtml(content)}</span>`);
      }
    });

    return lines.join('\n');
  }
}

class Terminal {
  constructor(canvasId, contentRenderer, cameraX = CONFIG.camera.position.x) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) {
      throw new Error(`Canvas element with id "${canvasId}" not found`);
    }

    this.contentRenderer = contentRenderer;
    this.cameraX = cameraX;
    this.scene = new THREE.Scene();
    this.scene.background = null;
    this.disposed = false;

    this.setupCamera();
    this.setupRenderers();
    this.setupControls();
    this.setupLighting();
    this.createTerminal();
    this.setupGround();
    this.setupAnimation();
    this.setupResponsive();

    this.updateResponsiveLayout();
  }

  /**
   * @param {number} cameraX
   * @param {{x: number, y: number, z: number}} position
   * @returns {number}
   */
  calculateCameraZWithConstantDistance(cameraX, position) {
    const targetDistance = Math.sqrt(position.x ** 2 + position.y ** 2 + position.z ** 2);
    const zSquared = targetDistance ** 2 - cameraX ** 2 - position.y ** 2;
    const MIN_SAFE_DISTANCE = 0.1;

    if (zSquared < 0) {
      console.warn('Camera position parameters would produce invalid distance. Using minimum safe value.');
      return MIN_SAFE_DISTANCE;
    }

    return Math.sqrt(zSquared);
  }

  /**
   * @returns {{width: number, height: number}}
   */
  getSafeCanvasDimensions() {
    const MIN_DIMENSION = 1;
    return {
      width: Math.max(this.canvas.clientWidth, MIN_DIMENSION),
      height: Math.max(this.canvas.clientHeight, MIN_DIMENSION)
    };
  }

  setupCamera() {
    const { fov, near, far, position } = CONFIG.camera;
    const { width, height } = this.getSafeCanvasDimensions();

    this.camera = new THREE.PerspectiveCamera(
      fov,
      width / height,
      near,
      far
    );

    const cameraZ = this.calculateCameraZWithConstantDistance(this.cameraX, position);

    this.camera.position.set(this.cameraX, position.y, cameraZ);
    this.camera.lookAt(0, 0, 0);
  }

  setupRenderers() {
    const { width, height } = this.getSafeCanvasDimensions();

    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    this.cssRenderer = new CSS3DRenderer();
    this.cssRenderer.setSize(width, height);
    this.cssRenderer.domElement.style.position = 'absolute';
    this.cssRenderer.domElement.style.top = '0';
    this.cssRenderer.domElement.style.pointerEvents = 'none';

    const parent = this.canvas.parentElement;
    if (!parent) {
      throw new Error('Canvas element must have a parent element');
    }
    parent.appendChild(this.cssRenderer.domElement);
  }

  setupControls() {
    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.enableZoom = false;
    this.controls.enablePan = false;
    this.controls.maxPolarAngle = Math.PI / 2;
    this.controls.enableRotate = true;
  }

  setupLighting() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);

    const lightXDirection = this.cameraX > 0 ? 8 : -8;
    const fillXDirection = this.cameraX > 0 ? -8 : 8;

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
    directionalLight.position.set(lightXDirection, 15, 8);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    this.scene.add(directionalLight);

    const fillLight = new THREE.DirectionalLight(CONFIG.colors.accent, 0.3);
    fillLight.position.set(fillXDirection, 8, -8);
    this.scene.add(fillLight);
  }

  createTerminal() {
    this.terminalGroup = new THREE.Group();

    this.createWindowFrame();
    this.createTitleBar();
    this.createControlButtons();
    this.createDisplay();
    this.createTerminalText();

    this.scene.add(this.terminalGroup);
  }

  createWindowFrame() {
    const { width, height, cornerRadius, depth } = CONFIG.terminal;
    const shape = createRoundedRectShape(width, height, cornerRadius);

    const geometry = new THREE.ExtrudeGeometry(shape, {
      depth,
      bevelEnabled: false,
    });

    const material = new THREE.MeshStandardMaterial({
      color: CONFIG.colors.surface,
      metalness: 0.1,
      roughness: 0.9,
    });

    const frame = new THREE.Mesh(geometry, material);
    frame.castShadow = true;
    frame.receiveShadow = true;
    this.terminalGroup.add(frame);
  }

  createTitleBar() {
    const { width, height, depth } = CONFIG.titleBar;
    const { cornerRadius, height: terminalHeight } = CONFIG.terminal;

    const shape = createRoundedRectShape(width, height, cornerRadius, {
      topLeft: true,
      topRight: true,
      bottomLeft: false,
      bottomRight: false,
    });

    const geometry = new THREE.ExtrudeGeometry(shape, {
      depth,
      bevelEnabled: false,
    });

    const material = new THREE.MeshStandardMaterial({
      color: CONFIG.colors.border,
      metalness: 0.1,
      roughness: 0.9,
    });

    const titleBar = new THREE.Mesh(geometry, material);
    titleBar.position.set(0, terminalHeight / 2 - height / 2, CONFIG.zIndex.titleBar);
    this.terminalGroup.add(titleBar);
  }

  createControlButtons() {
    const { radius, spacing, startX, colors } = CONFIG.buttons;
    const { width: terminalWidth, height: terminalHeight } = CONFIG.terminal;
    const { height: titleBarHeight } = CONFIG.titleBar;
    const yPos = terminalHeight / 2 - titleBarHeight / 2;
    const CIRCLE_SEGMENTS = 32;

    const buttonConfigs = [
      { color: colors.close, x: -terminalWidth / 2 + startX },
      { color: colors.minimize, x: -terminalWidth / 2 + startX + spacing },
      { color: colors.maximize, x: -terminalWidth / 2 + startX + spacing * 2 },
    ];

    buttonConfigs.forEach(({ color, x }) => {
      const geometry = new THREE.CircleGeometry(radius, CIRCLE_SEGMENTS);
      const material = new THREE.MeshBasicMaterial({ color });
      const button = new THREE.Mesh(geometry, material);
      button.position.set(x, yPos, CONFIG.zIndex.buttons);
      this.terminalGroup.add(button);
    });
  }

  createDisplay() {
    const { width, height, cornerRadius } = CONFIG.display;

    const shape = createRoundedRectShape(width, height, cornerRadius, {
      topLeft: false,
      topRight: false,
      bottomLeft: true,
      bottomRight: true,
    });

    const geometry = new THREE.ShapeGeometry(shape);
    const material = new THREE.MeshStandardMaterial({
      color: CONFIG.colors.black,
      metalness: 0,
      roughness: 1,
    });

    const display = new THREE.Mesh(geometry, material);
    display.position.set(0, -0.2, CONFIG.zIndex.display);
    this.terminalGroup.add(display);
  }

  createTerminalText() {
    const div = document.createElement('div');
    div.className = 'quadro-terminal-text';
    div.innerHTML = this.contentRenderer.render();

    this.terminalTextObject = new CSS3DObject(div);
    this.terminalTextObject.position.set(0, 0.05, CONFIG.zIndex.text);
    this.terminalTextObject.scale.set(CONFIG.textScale, CONFIG.textScale, CONFIG.textScale);

    this.terminalGroup.add(this.terminalTextObject);
  }

  setupGround() {
    const geometry = new THREE.PlaneGeometry(15, 15);
    const material = new THREE.ShadowMaterial({
      opacity: 0.2,
      color: 0x000000
    });
    this.ground = new THREE.Mesh(geometry, material);
    this.ground.rotation.x = -Math.PI / 2;
    this.ground.position.y = -2.5;
    this.ground.receiveShadow = true;
    this.scene.add(this.ground);
  }

  setupAnimation() {
    this.animationState = {
      time: 0,
      isRunning: false,
    };
  }

  setupResponsive() {
    const DEBOUNCE_DELAY_MS = 150;
    let resizeTimeout;

    this.resizeHandler = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => this.handleResize(), DEBOUNCE_DELAY_MS);
    };

    this.cleanupResize = () => {
      clearTimeout(resizeTimeout);
      window.removeEventListener('resize', this.resizeHandler);
    };

    window.addEventListener('resize', this.resizeHandler);
  }

  handleResize() {
    const { width, height } = this.getSafeCanvasDimensions();

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();

    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    this.cssRenderer.setSize(width, height);

    this.updateResponsiveLayout();
  }

  /**
   * Updates the responsive layout of the terminal based on container dimensions.
   * Applies proportional scaling with min/max bounds and mobile boost.
   */
  updateResponsiveLayout() {
    const {
      referenceWidth,
      referenceHeight,
      rotationClearance,
      scaleMin,
      scaleMax,
      groundPositionMultiplier,
    } = CONFIG.responsive;

    const { width: containerWidth, height: containerHeight } = this.getSafeCanvasDimensions();

    const scaleX = containerWidth / referenceWidth;
    const scaleY = containerHeight / referenceHeight;
    let baseScale = Math.min(scaleX, scaleY);

    const MOBILE_BREAKPOINT = 768;
    const TABLET_BREAKPOINT = 1024;
    const MOBILE_BOOST = 1.7;
    const TABLET_BOOST = 1.2;

    const viewportWidth = window.innerWidth;
    if (viewportWidth < MOBILE_BREAKPOINT) {
      baseScale *= MOBILE_BOOST;
    } else if (viewportWidth < TABLET_BREAKPOINT) {
      baseScale *= TABLET_BOOST;
    }

    const terminalScale = Math.max(scaleMin, Math.min(scaleMax, baseScale * rotationClearance));

    this.terminalGroup.scale.set(terminalScale, terminalScale, terminalScale);

    if (this.ground) {
      this.ground.position.y = groundPositionMultiplier * terminalScale;
    }

    if (this.terminalTextObject) {
      this.terminalTextObject.scale.set(CONFIG.textScale, CONFIG.textScale, CONFIG.textScale);
    }
  }

  animate() {
    if (!this.animationState.isRunning) {
      return;
    }

    this.animationId = requestAnimationFrame(() => this.animate());

    this.animationState.time += CONFIG.animation.rotationSpeed;

    const { rotationAmplitude } = CONFIG.animation;
    this.terminalGroup.rotation.y = Math.sin(this.animationState.time * 0.15) * rotationAmplitude.y;
    this.terminalGroup.rotation.x = Math.sin(this.animationState.time * 0.1) * rotationAmplitude.x;

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
    this.cssRenderer.render(this.scene, this.camera);
  }

  start() {
    this.animationState.isRunning = true;
    this.animate();
  }

  stop() {
    this.animationState.isRunning = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  dispose() {
    if (this.disposed) {
      return;
    }
    this.disposed = true;

    this.stop();

    if (this.cleanupResize) {
      this.cleanupResize();
    }

    if (this.controls) {
      this.controls.dispose();
    }

    if (this.renderer) {
      this.renderer.dispose();
    }

    if (this.cssRenderer && this.cssRenderer.domElement && this.cssRenderer.domElement.parentElement) {
      this.cssRenderer.domElement.parentElement.removeChild(this.cssRenderer.domElement);
    }

    if (this.ground) {
      if (this.ground.geometry) this.ground.geometry.dispose();
      if (this.ground.material) this.ground.material.dispose();
    }

    if (this.scene) {
      this.scene.traverse(object => {
        if (object.geometry) object.geometry.dispose();
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach(material => material.dispose());
          } else {
            object.material.dispose();
          }
        }
      });
    }
  }
}

const terminalScenes = {};

function initTerminalScenes() {
  const heroCanvas = document.getElementById('quadro-canvas');
  if (heroCanvas && !terminalScenes.hero) {
    try {
      const content = new TableContent(TERMINAL_DATA_HERO);
      const scene = new Terminal('quadro-canvas', content);
      scene.start();
      terminalScenes.hero = scene;
    } catch (error) {
      console.error('Failed to initialize hero terminal scene:', error);
    }
  }

  const mcpCanvas = document.getElementById('quadro-canvas-mcp');
  if (mcpCanvas && !terminalScenes.mcp) {
    try {
      const content = new ConversationContent(TERMINAL_DATA_MCP);
      const scene = new Terminal('quadro-canvas-mcp', content, -4);
      scene.start();
      terminalScenes.mcp = scene;
    } catch (error) {
      console.error('Failed to initialize MCP terminal scene:', error);
    }
  }
}

function cleanupTerminalScenes() {
  Object.values(terminalScenes).forEach(scene => {
    if (scene) scene.dispose();
  });
  Object.keys(terminalScenes).forEach(key => delete terminalScenes[key]);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTerminalScenes);
} else {
  initTerminalScenes();
}

if (typeof document$ !== 'undefined') {
  document$.subscribe(() => {
    const heroCanvas = document.getElementById('quadro-canvas');
    const mcpCanvas = document.getElementById('quadro-canvas-mcp');

    if (heroCanvas || mcpCanvas) {
      cleanupTerminalScenes();
      initTerminalScenes();
    } else {
      if (Object.keys(terminalScenes).length > 0) {
        cleanupTerminalScenes();
      }
    }
  });
}
