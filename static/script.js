gsap.registerPlugin(MorphSVGPlugin);

class NavbarAnimations {
  constructor({ buttonMap }) {
    this.buttonMap = buttonMap;
    this.buttonStates = new Map();
  }

  initialize() {
    for (const [svgId, parameters] of this.buttonMap) {
      // Create a state object for the current button.
      const state = {};
      for (const [parameter, parameter_value] of parameters.entries()) {
        state[parameter] = parameter_value;
      }

      // Pre-calculate and store initial paths and positions in the state object.
      state.buttonFillPath = document.getElementById(state.startButtonFillId.substring(1))?.getAttribute('d');
      state.buttonOutlinePath = document.getElementById(state.startButtonOutlineId.substring(1))?.getAttribute('d');
      state.buttonPositionX = parseFloat(document.getElementById(state.buttonTextContainerId.substring(1))?.getAttribute('x'));
      state.buttonPositionY = parseFloat(document.getElementById(state.buttonTextContainerId.substring(1))?.getAttribute('y'));

      // Save the complete state object, keyed by the button's main SVG ID.
      this.buttonStates.set(svgId, state);
      
      // Attach event listeners. The same handler methods will be used for all buttons.
      const svgButtonElement = document.getElementById(svgId);
      if (svgButtonElement.classList.contains('active')) {
        gsap.set(state.startButtonFillId, { morphSVG: state.endButtonFillId, fill: "url(#paint0_linear_0_1)" });
        gsap.set(state.startButtonOutlineId, { morphSVG: state.endButtonOutlineId });
        gsap.set(state.buttonTextContainerId, { x: state.buttonPositionX, y: "+=10" });
        gsap.set(state.buttonTextId, { fill: "white" });
      }
      
      else  {
      svgButtonElement.addEventListener('mouseleave', this.mouseLeave.bind(this));
      svgButtonElement.addEventListener('mouseenter', this.mouseEnter.bind(this));
      };
    }
  }

  // The event handler now uses the event object to find the correct state.
  mouseEnter(event) {
    const state = this.buttonStates.get(event.currentTarget.id);
    if (!state) return;

    gsap.killTweensOf([state.startButtonFillId, state.startButtonOutlineId, state.buttonTextContainerId]);

    gsap.to(state.startButtonFillId, { duration: 1, morphSVG: state.endButtonFillId, ease: "elastic.out(1, 0.3)" });
    gsap.to(state.startButtonOutlineId, { duration: 1, morphSVG: state.endButtonOutlineId, ease: "elastic.out(1, 0.3)" });
    gsap.set(state.startButtonFillId, { fill: "url(#paint0_linear_0_1)" });
    gsap.to(state.buttonTextContainerId, { duration: 1, x: state.buttonPositionX, y: "+=10", ease: "elastic.out(1, 0.3)" });
    gsap.set(state.buttonTextId, { fill: "white" });
  }

  // This handler also looks up state dynamically.
  mouseLeave(event) {
    const state = this.buttonStates.get(event.currentTarget.id);
    if (!state) return;

    gsap.killTweensOf([state.startButtonFillId, state.startButtonOutlineId, state.buttonTextContainerId]);

    gsap.to(state.startButtonFillId, { duration: 1, morphSVG: state.buttonFillPath, ease: "elastic.out(1, 0.3)" });
    gsap.to(state.startButtonOutlineId, { duration: 1, morphSVG: state.buttonOutlinePath, ease: "elastic.out(1, 0.3)" });
    gsap.set(state.startButtonFillId, { fill: "url(#paint1_linear_0_0)" });
    gsap.to(state.buttonTextContainerId, { duration: 1, x: state.buttonPositionX, y: state.buttonPositionY, ease: "elastic.out(1, 0.3)" });
    gsap.set(state.buttonTextId, { fill: "black" });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // This map defines the configuration for each button to animate.
  const buttonMap = new Map([
    ['nav-button-1', new Map([
      ['startButtonFillId', '#startHomeButtonFill'],
      ['startButtonOutlineId', '#startHomeButtonOutline'],
      ['endButtonFillId', '#endHomeButtonFill'],
      ['endButtonOutlineId', '#endHomeButtonOutline'],
      ['buttonTextContainerId', '#homeButtonTextContainer'],
      ['buttonTextId', '#homeButtonText']
    ])],
    ['nav-button-2', new Map([
      ['startButtonFillId', '#startWorkButtonFill'],
      ['startButtonOutlineId', '#startWorkButtonOutline'],
      ['endButtonFillId', '#endWorkButtonFill'],
      ['endButtonOutlineId', '#endWorkButtonOutline'],
      ['buttonTextContainerId', '#workButtonTextContainer'],
      ['buttonTextId', '#workButtonText']
    ])],
    ['nav-button-3', new Map([
      ['startButtonFillId', '#startBlogButtonFill'],
      ['startButtonOutlineId', '#startBlogButtonOutline'],
      ['endButtonFillId', '#endBlogButtonFill'],
      ['endButtonOutlineId', '#endBlogButtonOutline'],
      ['buttonTextContainerId', '#blogButtonTextContainer'],
      ['buttonTextId', '#blogButtonText']
    ])]
  ]);

  // Create an instance of the NavbarAnimations class with your button configuration.
  const navbarAnimation = new NavbarAnimations({ buttonMap });

  // Initialize the animations, which attaches the event listeners to the buttons.
  navbarAnimation.initialize();
});
