export default function WeatherMessage({message}: {message: string}) {
    return (
        <div className='warning'>
            {message}
        </div>
    );
}