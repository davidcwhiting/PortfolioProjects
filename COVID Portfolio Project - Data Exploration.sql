/*
Covid 19 Data Exploration

Skills used: Joins, CTE's, Temp Tables, Windows Functions, Aggregate Functions, Creating Views, Converting Data Types
*/

SELECT *
FROM [master].[dbo].[covidVaccinations]
where continent is not null
order by 3,4;

-- Select data that we are going to be starting with

Select Location,date, total_cases,new_cases, total_deaths,[population]
from [master].[dbo].[covidDeaths]
where continent is not null
order by 1,2;

--Total Cases vs Total Deaths
-- Shows likelihood of dying if you contract covid in your country

SELECT Location, date, total_cases,total_deaths,round(total_deaths/total_cases*100,1) as DeathPercentage
from [master].[dbo].[covidDeaths]
where location like '%states%'
and continent is not null
order by 1,2;

-- Countries with Histest Infection Rate vs Population

SELECT Location, Population, Max(total_cases) as HighestInfectionCount, round(Max((total_cases/population))*100,1) as PercentPopulationInfected
FROM [master].[dbo].[covidDeaths]
group by Location, Population
order by PercentPopulationInfected desc;

--Countries with Highest Death Count per Population

SELECT location, MAX(cast(Total_deaths as int)) as TotalDeathCount
from [master].[dbo].[covidDeaths]
where continent is not null
group by Location
order by TotalDeathCount desc;

--showing by continent

--continents with highest death count per population

SELECT continent, max(cast(Total_deaths as int)) as TotalDeathCount
from [master].[dbo].[covidDeaths]
where continent is not null
group by continent
order by TotalDeathCount desc;

--Global Numbers

SELECT sum(new_cases) as total_cases, sum(cast(new_deaths as int)) as total_deaths, round(sum(cast(new_deaths as int))/SUM(New_Cases)*100,1) as DeathPercentage
from [master].[dbo].[covidDeaths]
where continent is not null
--Group by date
order by 1,2;

--Total Population compared to Vaccinations
--Shows Percentage of Population that received at least one Vaccine

SELECT death.continent, death.location, death.date,death.population, vac.new_vaccinations,
sum(cast(vac.new_vaccinations as int)) OVER (Partition by death.Location Order by Death.Location, Death.Date) as RollingPeopleVaccinated
From [master].[dbo].[covidDeaths] death
join [master].[dbo].[covidVaccinations] vac
	on death.location = vac.location
	and death.date = vac.date
where death.continent is not null
order by 2,3

-- Using CTE to perform Calculation on Partition By in previous query

WITH PopvsVac (Continent, Location, Date, Population, New_Vaccinations, RollingPeopleVaccinated)
as
(SELECT death.continent, death.location, death.date,death.population, vac.new_vaccinations,
sum(cast(vac.new_vaccinations as int)) OVER (Partition by death.Location Order by Death.Location, Death.Date) as RollingPeopleVaccinated
From [master].[dbo].[covidDeaths] death
join [master].[dbo].[covidVaccinations] vac
	on death.location = vac.location
	and death.date = vac.date
where death.continent is not null)

select *, ROUND((RollingPeopleVaccinated/Population)*100,1) as percent_pop_vacc
from PopvsVac

--Using Temp Table to perform Calculation on Partition By in previous Query
DROP TABLE if exists #PercentPopulationVaccinated
CREATE TABLE #PercentPopulationVaccinated
(Continent nvarchar(255),
Location nvarchar(255),
Date datetime,
Population numeric,
New_vaccinations numeric,
RollingPeopleVaccinated numeric)

Insert into #PercentPopulationVaccinated
SELECT death.continent, death.location, death.date,death.population, vac.new_vaccinations,
sum(convert(Bigint,vac.new_vaccinations)) OVER (Partition by death.Location Order by Death.Location, Death.Date) as RollingPeopleVaccinated
From [master].[dbo].[covidDeaths] death
join [master].[dbo].[covidVaccinations] vac
	on death.location = vac.location
	and death.date = vac.date
where death.continent is not null

-- Creating View which stores data for later vizualizations

CREATE VIEW PercentPopulationVaccinated as
SELECT death.continent, death.location, death.date,death.population, vac.new_vaccinations,
sum(convert(Bigint,vac.new_vaccinations)) OVER (Partition by death.Location Order by Death.Location, Death.Date) as RollingPeopleVaccinated
From [master].[dbo].[covidDeaths] death
join [master].[dbo].[covidVaccinations] vac
	on death.location = vac.location
	and death.date = vac.date
where death.continent is not null
