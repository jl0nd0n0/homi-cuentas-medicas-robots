const { exec } = require('child_process');

// Obtener la fecha actual
const now = new Date();
const dia = String(now.getDate()).padStart(2, '0');
const mes = String(now.getMonth() + 1).padStart(2, '0');
const anio = String(now.getFullYear());

const batchFilePath = 'C:\\tools\\robots\\homi\\wrapper-automation\\factura_dia\\robot.bat';

const comando = `"${batchFilePath}" ${dia} ${mes} ${anio}`;

exec(comando, (error, stdout, stderr) => {
    if (error) {
        console.error(`Error ejecutando el batch: ${error.message}`);
        return;
    }
    if (stderr) {
        console.error(`stderr: ${stderr}`);
        return;
    }
    console.log(`Salida:\n${stdout}`);
});
