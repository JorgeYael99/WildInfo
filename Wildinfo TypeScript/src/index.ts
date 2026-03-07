import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors({
  origin: '*',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['*'],
}));

app.get('/', (_req: Request, res: Response) => {
  res.json({ message: 'Servidor WildInfo Arriba', status: 200 });
});

interface Taxonomy {
  kingdom: string;
  class: string;
  family: string;
}

interface AnimalData {
  name: string;
  taxonomy: Taxonomy;
}

interface AnimalResponse {
  nombre: string;
  reino: string;
  clase: string;
  familia: string;
}

app.get('/wildinfo/:name_or_id', async (req: Request, res: Response): Promise<void> => {
  const { name_or_id } = req.params;
  const externalUrl = `https://api.api-ninjas.com/v1/animals?name=${name_or_id.toLowerCase()}`;
  const apiKey = process.env.API_NINJS_KEY || '';

  try {
    const response = await axios.get<AnimalData[]>(externalUrl, {
      headers: { 'X-Api-Key': apiKey },
    });

    console.log(`DEBUG EXTERNO: Ninjas API respondió con ${response.status}`);

    if (response.status === 404 || response.data.length === 0) {
      res.status(404).json({ detail: 'animal no encontrado' });
      return;
    }

    const animalData: AnimalResponse = {
      nombre: response.data[0].name,
      reino: response.data[0].taxonomy.kingdom,
      clase: response.data[0].taxonomy.class,
      familia: response.data[0].taxonomy.family,
    };

    res.json(animalData);
  } catch (error) {
    if (axios.isAxiosError(error) && error.code === 'ECONNREFUSED') {
      res.status(503).json({ detail: 'Servicio externo no disponible' });
    } else {
      res.status(500).json({ detail: 'Error interno del servidor' });
    }
  }
});

app.use((req: Request, res: Response, next: NextFunction) => {
  const startTime = Date.now();
  
  res.on('finish', () => {
    const processTime = Date.now() - startTime;
    console.log(`DEBUG: ${req.method} ${req.path} - Status: ${res.statusCode} - ${processTime}ms`);
  });
  
  next();
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
  });
}

export default app;
