export interface IklimData {
    labels: string[];
    values: number[][];
    type: string;
}

export const parseIklimContent = (content: string, fileType: string): IklimData => {
    const lines = content.split('\n');
    
    const labels: string[] = [];
    const tMax: number[] = [];
    const tMin: number[] = [];

    // Cara yang lebih aman: Lewati baris yang tidak mengandung angka tahun/data
    lines.forEach((line) => {
        const trimmedLine = line.trim();
        // Regex ini mengecek apakah baris dimulai dengan 4 digit angka (Tahun)
        // Format SWAT+ biasanya: "YYYY  DOY    VALUE"
        if (/^\d{4}/.test(trimmedLine)) {
            const parts = trimmedLine.split(/\s+/).filter(Boolean);
            
            if (parts.length >= 4) {
                labels.push(`${parts[1]}-${parts[0]}`);
                tMax.push(parseFloat(parts[2]));
                tMin.push(parseFloat(parts[3]));
            } else if (parts.length === 3) {
                // Jika kolom ke-4 hilang, isi dengan 0 agar panjang array tetap sama
                labels.push(`${parts[1]}-${parts[0]}`);
                tMax.push(parseFloat(parts[2]));
                tMin.push(0); 
            }
        }
    });
    
    return { labels, values: [tMax, tMin], type: fileType };
};