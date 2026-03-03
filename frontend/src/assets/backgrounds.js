// Importa todas as imagens de fundo para que o Vite as processe corretamente
import loginBg from './login_background.png';
import bestiaryBg from './bestiary_background.png';
import fichasBg from './fichas_background.png';
import editFichaBg from './edit_ficha_background.png';
import salasBg from './salas_background.png';
import salaBg from './sala-background.png';
import mestreBg from './mestre_background.png';
import cantigasBg from './cantigas_background.png';
import ferrariaBg from './ferraria_background.png';

export const backgrounds = {
  login: loginBg,
  bestiario: bestiaryBg,
  fichas: fichasBg,
  editFicha: editFichaBg,
  salas: salasBg,
  sala: salaBg,
  mestre: mestreBg,
  cantigas: cantigasBg,
  ferraria: ferrariaBg,
};

export function useBackground(key) {
  return () => {
    document.body.style.backgroundImage = `url(${backgrounds[key]})`;
    document.body.style.backgroundSize = 'cover';
    document.body.style.backgroundPosition = 'center';
    document.body.style.backgroundAttachment = 'fixed';
    return () => { document.body.style.backgroundImage = ''; };
  };
}