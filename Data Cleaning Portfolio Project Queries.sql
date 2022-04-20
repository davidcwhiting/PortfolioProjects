
/*
Cleaning Data in SQL Queries
*/

SELECT *
FROM master.dbo.NashvilleHousing;

--------------------------------------------------------------------------------------------------------------
--Standardized Date Format

ALTER TABLE NashvilleHousing
ADD SaleDateConverted Date;

UPDATE NashvilleHousing
SET SaleDateConverted = CONVERT(Date,SaleDate)

SELECT SaleDateConverted, CONVERT(Date,SaleDate)
FROM master.dbo.NashvilleHousing;

--------------------------------------------------------------------------------------------------------------
--Populate Property Address Data

SELECT *
from master.dbo.NashvilleHousing
--where PropertyAddress is null;
order by ParcelID


SELECT a.ParcelID,a.PropertyAddress, b.ParcelID, b.PropertyAddress,ISNULL(a.PropertyAddress,b.PropertyAddress)
from master.dbo.NashvilleHousing a
JOIN master.dbo.NashvilleHousing b
	on a.ParcelID=b.ParcelID
	and a.[uniqueID] <> b.[uniqueID]
where a.PropertyAddress is null;


UPDATE a
SET PropertyAddress = ISNULL(a.PropertyAddress,b.PropertyAddress)
from master.dbo.NashvilleHousing a
JOIN master.dbo.NashvilleHousing b
	on a.ParcelID=b.ParcelID
	and a.[uniqueID] <> b.[uniqueID];

--------------------------------------------------------------------------------------------------------------
--Breaking out address into individual columns (Address, City, State)

SELECT PropertyAddress
from master.dbo.NashvilleHousing;

SELECT 
SUBSTRING(PropertyAddress,1, CHARINDEX(',',PropertyAddress)-1) as Address,
SUBSTRING(PropertyAddress, CHARINDEX(',',PropertyAddress)+1,LEN(PropertyAddress)) as City
from master.dbo.NashvilleHousing;

ALTER TABLE NashvilleHousing
ADD PropertySplitAddress Nvarchar(255);

UPDATE NashvilleHousing
SET PropertySplitAddress = SUBSTRING(PropertyAddress,1, CHARINDEX(',',PropertyAddress)-1)

ALTER TABLE NashvilleHousing
ADD PropertySplitCity Nvarchar(255);

UPDATE NashvilleHousing
SET PropertySplitCity = SUBSTRING(PropertyAddress, CHARINDEX(',',PropertyAddress)+1,LEN(PropertyAddress))

--------------------------------------------------------------------------------------------------------------
--Breaking out OwnderAddress into individual columns (Address, City, State)

SELECT OwnerAddress
from master.dbo.NashvilleHousing;

SELECT 
PARSENAME(REPLACE(OwnerAddress,',','.'),3),
PARSENAME(REPLACE(OwnerAddress,',','.'),2),
PARSENAME(REPLACE(OwnerAddress,',','.'),1)
from master.dbo.NashvilleHousing;


ALTER TABLE NashvilleHousing
ADD OwnerSplitAddress Nvarchar(255);

UPDATE NashvilleHousing
SET OwnerSplitAddress = PARSENAME(REPLACE(OwnerAddress,',','.'),3)

ALTER TABLE NashvilleHousing
ADD OwnerSplitCity Nvarchar(255);

UPDATE NashvilleHousing
SET OwnerSplitCity = PARSENAME(REPLACE(OwnerAddress,',','.'),2)

ALTER TABLE NashvilleHousing
ADD OwnerSplitState Nvarchar(255);

UPDATE NashvilleHousing
SET OwnerSplitState = PARSENAME(REPLACE(OwnerAddress,',','.'),3)

--------------------------------------------------------------------------------------------------------------
--Change Y and N to Yes and No in "Sold as Vacant' Field

SELECT Distinct(SoldAsVacant),Count(SoldAsVacant)
from master.dbo.NashvilleHousing
group by SoldAsVacant
order by 2

SELECT SoldAsVacant,
CASE when SoldAsVacant = 'Y' then 'Yes'
	 when SoldAsVacant = 'N' then 'No'
	 ELSE SoldAsVacant
	 END
FROM master.dbo.NashvilleHousing


Update NashvilleHousing
set SoldAsVacant=CASE when SoldAsVacant = 'Y' then 'Yes'
	when SoldAsVacant = 'N' then 'No'
	ELSE SoldAsVacant
	END;
--------------------------------------------------------------------------------------------------------------
--Remove Duplicates

WITH RowNumCTE as(
SELECT *,
		ROW_NUMBER() OVER (
		PARTITION BY ParcelID,
					 PropertyAddress,
					 SalePrice, 
					 SaleDate, 
					 LegalReference 
					 ORDER BY 
					 UniqueID) row_num
FROM master.dbo.NashvilleHousing
--ORDER BY ParcelID
)

DELETE 
FROM RowNumCTE
WHERE row_num > 1
--order by PropertyAddress;

--------------------------------------------------------------------------------------------------------------
-- Delete Unused Columns

Select *
FROM master.dbo.NashvilleHousing

ALTER TABLE master.dbo.NashvilleHousing
DROP COLUMN OwnerAddress, TaxDistrict, PropertyAddress, SaleDate
