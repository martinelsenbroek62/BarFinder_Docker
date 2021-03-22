import JSZip from 'jszip';

export function makeDownload(fileName, mediaType, data, isBlob = false) {
    if (typeof (document) === 'undefined') {
        return;
    }
    if (!isBlob) {
        data = new Uint8Array(Array.from(data).map((c) => c.charCodeAt(0)));
        data = new Blob([data], {type: mediaType});
    }
    let uri = URL.createObjectURL(data);
    if (window.navigator.msSaveOrOpenBlob) {
        // download method of IE
        window.navigator.msSaveOrOpenBlob(data, fileName);
    } else if (fileName.endsWith('.xml') && data.size < 1024 * 1024) {
        // open small XML in browser instead of downloading it
        window.location = uri;
    } else {
        let a = document.createElement('a');

        // firefox required a tag being attached to document
        a.style.display = 'none';
        document.body.appendChild(a);

        a.setAttribute('href', uri);
        a.setAttribute('download', fileName);
        a.click();
        setTimeout(() => document.body.removeChild(a));
    }
}

function csvwriter(rows) {
    const output = [];
    for (const row of rows) {
        const csvrow = [];
        for (let cell of row) {
            cell = String(cell);
            if (cell.indexOf('"') > -1) {
                cell = `"${cell.replace(/"/g, '\\"')}"`;
            }
            csvrow.push(cell);
        }
        output.push(csvrow.join(','));
        output.push('\n');
    }
    return new Blob([
        new Uint8Array([0xEF, 0xBB, 0xBF]), // UTF-8 BOM
        output.join('')
    ], {type: 'text/plain;charset=utf-8'});
}

export function makeCSVDownload(fileName, rows) {
    makeDownload(fileName, 'text/csv', csvwriter(rows), true);
}


export async function makeZIPDownload(fileName, files) {
    let zip = new JSZip();
    let zipFiles = zip.folder(fileName.replace(/\.zip$/, ''));
    files.forEach(({fileName, mediaType, data}) => {
        let blob = data;
        if (mediaType) {
            blob = new Blob([blob], {type: mediaType});
        }
        zipFiles.file(fileName, blob)
    });
    const zipBlob = await zip.generateAsync({
        type: 'blob',
        compression: "DEFLATE",
        compressionOptions: {level: 1}
    });
    makeDownload(fileName, 'application/zip', zipBlob, true);
}

export async function makeMultipleCSVDownload(fileName, files) {
    files = files.map(({fileName, rows}) => ({
        fileName,
        data: csvwriter(rows)
    }));
    makeZIPDownload(fileName, files);
}

export function makeJSONDownload(fileName, data) {
    makeDownload(
        fileName, 'application/json;charset=utf-8',
        JSON.stringify(data, null, 2)
    );
}
