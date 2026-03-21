import Game from "./game.js";

class StartScreen extends Game {
    init() {
        super.init();
        this.onMenuLoaded();
    }

    onMenuLoaded() {
        document.addEventListener('game.move_down', () => {
            document.querySelector('.current-choice').classList.remove('current-choice');
            const previousChoice = document.querySelector('.choices .choice:last-child');
            previousChoice.classList.add('current-choice');
        });

        document.addEventListener('game.move_up', () => {
            document.querySelector('.current-choice').classList.remove('current-choice');
            const nextChoice = document.querySelector('.choices .choice:first-child');
            nextChoice.classList.add('current-choice');
        });

        document.addEventListener('game.action', () => {
            const currentChoice = document.querySelector('.current-choice');
            const callbackName = currentChoice.getAttribute('data-callback');
            if (typeof this[callbackName] === 'function') {
                this[callbackName]();
            }
        });
    }

    async start() {
        await this.onShutdown();
        location.href = '/map';
    }

    openOptions() {
        console.log("Options opened");
        // Open options menu logic here
    }
}

const startScreen = new StartScreen();
export { startScreen };